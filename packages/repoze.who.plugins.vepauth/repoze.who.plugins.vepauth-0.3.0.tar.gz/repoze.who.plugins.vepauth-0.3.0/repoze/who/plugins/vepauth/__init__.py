# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
"""

A repoze.who plugin for automated authentication via BrowserID:

    https://browserid.org/
    https://wiki.mozilla.org/Identity/BrowserIDSync


This plugin implements an experimental protocol for authenticating to ReSTful
web services with the Verified Email Protocol, a.k.a Mozilla's BrowserID
project.  It is designed for use in automated tools like the Firefox Sync
Client.  If you're looking for something to use for human visitors on your
site, please try:

    http://github.com/mozilla-services/repoze.who.plugins.browserid

"""

__ver_major__ = 0
__ver_minor__ = 3
__ver_patch__ = 0
__ver_sub__ = ""
__ver_tuple__ = (__ver_major__, __ver_minor__, __ver_patch__, __ver_sub__)
__version__ = "%d.%d.%d%s" % __ver_tuple__


import re
import json
import time
import fnmatch

from zope.interface import implements

from webob import Request as Request_, Response

from repoze.who.interfaces import IIdentifier, IAuthenticator, IChallenger
from repoze.who.utils import resolveDotted

import vep
from vep.utils import get_assertion_info

from repoze.who.plugins.vepauth.tokenmanager import SignedTokenManager
from repoze.who.plugins.vepauth.noncemanager import NonceManager
from repoze.who.plugins.vepauth.utils import (strings_differ,
                                              parse_authz_header,
                                              check_mac_signature)


class VEPAuthPlugin(object):
    """Plugin to implement VEP-Auth in Repoze.who.

    This class provides an IIdentifier, IChallenger and IAuthenticator
    implementation of repoze.who.  Authentication is based on exchanging
    a VEP assertion for a short-lived session token, which is then used
    to sign requests using HTTP MAC Authentication.

    The class takes different parameters when instanciated:

    :param audiences: the intended audiences for the browserid assertions
    :param token_url: the url to use to retrieve the token. (defaults to
                      /request_token)
    :param token_manager: the class to make and parse tokens
    :param verifier: the vep.verifiers verifier to use
    :param nonce_timeout: the timeout for the nonce (defaults to 5mn) which
                          will be used in the MAC authentication flow

    """

    implements(IIdentifier, IChallenger, IAuthenticator)

    def __init__(self, audiences, token_url=None, token_manager=None,
                 verifier=None, nonce_timeout=None):
        if isinstance(audiences, basestring):
            raise ValueError("\"audiences\" must be a list of strings")
        # Fill in default values for any unspecified arguments.
        # I'm not declaring defaults on the arguments themselves because
        # we would then have to duplicate those defaults into make_plugin.
        if token_url is None:
            token_url = "/request_token"
        if token_manager is None:
            token_manager = SignedTokenManager()
        if verifier is None:
            verifier = vep.RemoteVerifier()
        if nonce_timeout is None:
            nonce_timeout = 60
        # Now we can initialize.
        self.audiences = audiences
        if audiences:
            audience_patterns = map(self._compile_audience_pattern, audiences)
            self._audience_patterns = audience_patterns
        self.token_url = token_url
        self.token_manager = token_manager
        self.verifier = verifier
        try:
            token_timeout = token_manager.timeout
        except AttributeError:
            token_timeout = None
        self.nonce_timeout = nonce_timeout
        self.nonce_manager = NonceManager(nonce_timeout, token_timeout)

    def identify(self, environ):
        """Extract the authentication info from the request.

        If this is a request to the token-provisioning URL then we extract
        a BrowserID assertion and exchange it for a new session token, setting
        environ["repoze.who.application"] so we can pass the token details
        back to the caller.

        For all other URLs, we extract the MAC params from the Authorization
        header and return those as the identity.
        """
        request = Request(environ)
        if self._is_request_to_token_url(request):
            return self._process_vep_assertion(request)
        return self._identify_mac(request)

    def remember(self, environ, identity):
        """Remember the user's identity.

        This is a no-op for this plugin; the client is supposed to remember
        the provisioned MAC credentials and re-use them for subsequent
        requests.
        """
        return []

    def forget(self, environ, identity):
        """Forget the user's identity.

        This simply issues a new WWW-Authenticate challenge, which should
        cause the client to forget any previously-provisioned credentials.
        """
        challenge = "MAC+BrowserID url=\"%s\"" % (self.token_url,)
        return [("WWW-Authenticate", challenge)]

    def challenge(self, environ, status, app_headers=(), forget_headers=()):
        """Challenge the user for credentials.

        This simply sends a 401 response using the WWW-Authenticate field
        as constructed by forget().
        """
        resp = Response()
        resp.status = 401
        resp.headers = self.forget(environ, {})
        for headers in (app_headers, forget_headers):
            for name, value in headers:
                resp.headers[name] = value
        resp.content_type = "text/plain"
        resp.body = "Unauthorized"
        return resp

    def authenticate(self, environ, identity):
        """Authenticate the extracted identity.

        The identity must be a set of MAC auth credentials extracted from
        the request.  This method checks the MAC signature, and if valid
        extracts the user metadata from the token.
        """
        request = Request(environ)
        assert not self._is_request_to_token_url(request)
        return self._authenticate_mac(request, identity)

    #
    #  Methods for exchanging an assertion for a MAC session token.
    #

    def _process_vep_assertion(self, request):
        """Exhange a VEP assertion for some session credentials.

        This  method extracts a submitted VEP assertion, validates it and
        establishes a new session token and secret.  These are returned
        to the user so that they can sign subsequent requests as belonging
        to this session.
        """
        # Make sure they're using a GET request.
        if request.method != "GET":
            resp = Response()
            resp.status = 405
            resp.content_type = "text/plain"
            resp.body = "token requests must get GET"
            request.environ["repoze.who.application"] = resp
            return None
        # Make sure they're sending an Authorization header.
        if not request.authorization:
            msg = "you must provide an authorization header"
            return self._respond_unauthorized(request, msg)
        # Grab the assertion from the Authorization header.
        scheme, assertion = request.authorization
        if scheme.lower() != "browser-id":
            msg = "The auth scheme \"%s\" is not supported" % (scheme,)
            return self._respond_bad_request(request, msg.encode("utf8"))
        # Extract the audience, so we can check against wildcards.
        try:
            audience = get_assertion_info(assertion)["audience"]
        except (ValueError, KeyError):
            return self._respond_bad_request(request, "invalid assertion")
        if not self._check_audience(request, audience):
            msg = "The audience \"%s\" is not acceptable" % (audience,)
            return self._respond_bad_request(request, msg.encode("utf8"))
        # Verify the assertion and find out who they are.
        try:
            data = self.verifier.verify(assertion)
        except Exception, e:
            msg = "Invalid BrowserID assertion: " + str(e)
            return self._respond_bad_request(request, msg)
        # OK, we can go ahead and issue a token.
        token, secret, extra = self.token_manager.make_token(request, data)

        if token is None:
            msg = "that email address is not recognised"
            return self._respond_unauthorized(request, msg)
        resp = Response()
        resp.status = 200
        resp.content_type = "application/json"

        body = {
            "id": token,
            "key": secret,
            "algorithm": "hmac-sha-1",
        }

        if extra is not None:
            body.update(extra)

        resp.body = json.dumps(body)
        request.environ["repoze.who.application"] = resp

    def _check_audience(self, request, audience):
        """Check that the audience is valid according to our configuration.

        This function uses the configured list of valid audience patterns to
        verify the given audience.  If no audience values have been configured
        then it matches against the Host header from the request.
        """
        if not self.audiences:
            return audience == request.host_url
        for audience_pattern in self._audience_patterns:
            if audience_pattern.match(audience):
                return True
        return False

    def _compile_audience_pattern(self, pattern):
        """Compile a glob-style audience pattern into a regular expression."""
        re_pattern = fnmatch.translate(pattern)
        if "://" not in pattern:
            re_pattern = "[a-z]+://" + re_pattern
        return re.compile(re_pattern)

    #
    #  Methods for MAC Authentication once the assertion has been verified.
    #

    def _identify_mac(self, request):
        """Parse, validate and return the request's MAC parameters.

        This method grabs the MAC credentials from the Authorization header
        and performs some sanity-checks.  If the credentials are missing or
        malformed then it returns None; if they're ok then they are returned
        in a dict.

        Note that this method does *not* validate the MAC signature.
        """
        params = parse_authz_header(request, None)
        if params is None:
            return None
        if params.get("scheme") != "MAC":
            return None
        # Check that various parameters are as expected.
        token = params.get("id")
        if token is None:
            msg = "missing MAC id"
            return self._respond_unauthorized(request, msg)
        # Check the timestamp and nonce for freshness or reuse.
        # TODO: the spec requires us to adjust for per-client clock skew.
        try:
            timestamp = int(params["ts"])
        except (KeyError, ValueError):
            msg = "missing or malformed MAC timestamp"
            return self._respond_unauthorized(request, msg)
        nonce = params.get("nonce")
        if nonce is None:
            msg = "missing MAC nonce"
            return self._respond_unauthorized(request, msg)
        if not self.nonce_manager.is_fresh(token, timestamp, nonce):
            msg = "MAC has stale token or nonce"
            return self._respond_unauthorized(request, msg)
        # OK, they seem like sensible MAC paramters.
        return params

    def _authenticate_mac(self, request, identity):
        # Check that these are MAC auth credentials.
        # They may not be if we're using multiple auth methods.
        if identity.get("scheme") != "MAC":
            return None
        token = identity["id"]
        # Decode the token.
        try:
            data, secret = self.token_manager.parse_token(token)
        except ValueError:
            msg = "invalid MAC id"
            return self._respond_unauthorized(request, msg)
        # Check the MAC signature.
        if not check_mac_signature(request, secret, identity):
            msg = "invalid MAC signature"
            return self._respond_unauthorized(request, msg)
        # Store the nonce to avoid re-use.
        # We do this *after* successul auth to avoid DOS attacks.
        nonce = identity["nonce"]
        timestamp = int(identity["ts"])
        self.nonce_manager.add_nonce(token, timestamp, nonce)
        # Update the identity with the data from the token.
        identity.update(data)
        return identity["repoze.who.userid"]

    #
    #  Misc helper methods.
    #

    def _respond_bad_request(self, request, message="Bad Request"):
        """Generate a "400 Bad Request" error response."""
        resp = Response()
        resp.status = 400
        resp.body = message
        request.environ["repoze.who.application"] = resp
        return None

    def _respond_unauthorized(self, request, message="Unauthorized"):
        """Generate a "401 Unauthorized" error response."""
        resp = Response()
        resp.status = 401
        resp.headers = self.forget(request.environ, {})
        resp.content_type = "text/plain"
        resp.body = message
        request.environ["repoze.who.application"] = resp
        return None

    def _is_request_to_token_url(self, request):
        """Check if given request is to the token-provisioning URL."""
        if not self.token_url:
            return False

        if self.token_url == request.path:
            return True

        request.match(self.token_url)

        if request.matchdict:
            return True

        return False


def make_plugin(audiences=None, token_url=None, nonce_timeout=None, **kwds):
    """Make a VEPAuthPlugin using values from a .ini config file.

    This is a helper function for loading a VEPAuthPlugin via the
    repoze.who .ini config file system. It converts its arguments from
    strings to the appropriate type then passes them on to the plugin.
    """
    # You *must* specify the "audiences" parameter since it's integral
    # to the security of the protocol.  If you want it set to None to
    # allow checking based on HTTP_HOST, set it to the empty string.
    if audiences is None:
        raise ValueError('You must specify the "audiences" parameter')
    if not audiences:
        audiences = None
    elif isinstance(audiences, basestring):
        audiences = audiences.split()
    # Load the token manager, possibly from a class+args.
    token_manager = _load_from_callable("token_manager", kwds)
    # Load the VEP verifier, possibly from a class+args.
    # Assume "urlopen" is a dotted-name of a callable.
    verifier = _load_from_callable("verifier", kwds, converters={
        "urlopen": resolveDotted
    })
    # If there are any kwd args left over, that's an error.
    for unknown_kwd in kwds:
        raise TypeError("unknown keyword argument: %s" % unknown_kwd)
    plugin = VEPAuthPlugin(audiences, token_url, token_manager, verifier,
                           nonce_timeout)
    return plugin


def _load_from_callable(name, kwds, converters={}):
    """Load a plugin argument from dotted python name of callable.

    This function is a helper to load and possibly instanciate an argument
    to the plugin.  It grabs the value from the dotted python name found in
    kwds[name].  If this is a callable, it it looks for arguments of the form
    kwds[name_*] and calls the object with them.
    """
    # See if we actually have the named object.
    dotted_name = kwds.pop(name, None)
    if dotted_name is None:
        return None
    obj = resolveDotted(dotted_name)
    # Extract any arguments for the callable.
    obj_kwds = {}
    prefix = name + "_"
    for key in kwds.keys():
        if key.startswith(prefix):
            obj_kwds[key[len(prefix):]] = kwds.pop(key)
    # To any type conversion on the arguments.
    for key, value in obj_kwds.iteritems():
        converter = converters.get(key)
        if converter is not None:
            obj_kwds[key] = converter(value)
    # Call it if callable.
    if callable(obj):
        obj = obj(**obj_kwds)
    elif obj_kwds:
        raise ValueError("arguments provided for non-callable %r" % (name,))
    return obj


class Request(Request_):
    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.matchdict = {}

    def match(self, route):
        """Set the matchdict parameter given a route"""
        regexp = re.sub(r"\{([a-zA-Z][^\}]*)\}", r"(?P<\1>([^}]+))", route)
        r = re.match(regexp, self.path)
        if r is not None:
            self.matchdict = r.groupdict()
