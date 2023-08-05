import base64
import hmac
import time
import urllib
from hashlib import sha1

try:
    import jwt
except:
    from twilio.contrib import jwt


class RequestValidator(object):

    def __init__(self, token):
        self.token = token

    def compute_signature(self, uri, params):
        """Compute the signature for a given request

        :param uri: full URI that Twilio requested on your server
        :param params: post vars that Twilio sent with the request
        :param auth: tuple with (account_sid, token)

        :returns: The computed signature
        """
        s = uri
        if len(params) > 0:
            for k, v in sorted(params.items()):
                s += k + v

        # compute signature and compare signatures
        computed = base64.encodestring(hmac.new(self.token, s, sha1).digest())
        return computed.strip()

    def validate(self, uri, params, signature):
        """Validate a request from Twilio

        :param uri: full URI that Twilio requested on your server
        :param params: post vars that Twilio sent with the request
        :param signature: expexcted signature in HTTP X-Twilio-Signature header
        :param auth: tuple with (account_sid, token)

        :returns: True if the request passes validation, False if not
        """
        return self.compute_signature(uri, params) == signature


class TwilioCapability(object):
    """
    A token to control permissions with Twilio Client

    :param string account_sid: the account sid to which this token
                               is granted access
    :param string auth_token: the secret key used to sign the token.
                              Note, this auth token is not visible to the
                              user of the token.

    :returns: A new TwilioCapability with zero permissions
    """

    def __init__(self, account_sid, auth_token):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.capabilities = {}
        self.client_name = None

    def payload(self):
        """Return the payload for this token."""
        if "outgoing" in self.capabilities and self.client_name is not None:
            scope = self.capabilities["outgoing"]
            scope.params["clientName"] = self.client_name

        capabilities = self.capabilities.values()
        scope_uris = [str(scope_uri) for scope_uri in capabilities]

        return {
            "scope": " ".join(scope_uris)
        }

    def generate(self, expires=3600):
        """Generate a valid JWT token with an expiration date.

        :param int expires: The token lifetime, in seconds. Defaults to
                            1 hour (3600)

        """
        payload = self.payload()
        payload['iss'] = self.account_sid
        payload['exp'] = int(time.time() + expires)
        return jwt.encode(payload, self.auth_token, "HS256")

    def allow_client_outgoing(self, application_sid, **kwargs):
        """Allow the user of this token to make outgoing connections.

        Keyword arguments are passed to the application.

        :param string application_sid: Application to contact
        """
        scope_params = {
            "appSid": application_sid,
        }
        if kwargs:
            scope_params["appParams"] = urllib.urlencode(kwargs, doseq=True)

        self.capabilities["outgoing"] = ScopeURI("client", "outgoing",
                                                 scope_params)

    def allow_client_incoming(self, client_name):
        """If the user of this token should be allowed to accept incoming
        connections then configure the TwilioCapability through this method and
        specify the client name.

        :param string client_name: Client name to accept calls from

        """
        self.client_name = client_name
        self.capabilities["incoming"] = ScopeURI("client", "incoming", {
            'clientName': client_name
        })

    def allow_event_stream(self, **kwargs):
        """Allow the user of this token to access their event stream."""
        scope_params = {
            "path": "/2010-04-01/Events",
        }
        if kwargs:
            scope_params['params'] = urllib.urlencode(kwargs, doseq=True)

        self.capabilities["events"] = ScopeURI("stream", "subscribe",
                                               scope_params)


class ScopeURI(object):

    def __init__(self, service, privilege, params=None):
        self.service = service
        self.privilege = privilege
        self.params = params

    def __str__(self):
        params = urllib.urlencode(self.params) if self.params else None
        param_string = "?%s" % params if params else ''
        return "scope:%s:%s%s" % (self.service, self.privilege, param_string)
