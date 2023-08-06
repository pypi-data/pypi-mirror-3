import requests
from oauth_hook import OAuthHook


class NetDNAOAuthHook(OAuthHook):

    def __init__(self, consumer_key, consumer_secret, token=None,
                 token_secret=None, header_auth=True, **kwargs):
        super(NetDNAOAuthHook, self).__init__(token, token_secret,
                                              consumer_key, consumer_secret,
                                              header_auth)


class NetDNA(object):

    def __init__(self, company_alias, key, secret,
                 server='rws.netdna.com', secure_connection=True, **kwargs):
        self.company_alias = company_alias
        self.server = server
        self.secure_connection = secure_connection
        self.client = requests.session(
                        hooks={
                          'pre_request': NetDNAOAuthHook(key, secret, **kwargs)
                        }
                      )

    @property
    def _connection_type(self):
        if self.secure_connection:
            return "https"
        return "http"

    def _get_url(self, uri):
        return "%s://%s/%s%s" % (
                                  self._connection_type,
                                  self.server,
                                  self.company_alias,
                                  uri
                                )

    def _response_as_json(self, method, uri, **kwargs):
        if kwargs.pop('debug', False):
            print "Making %s request to %s\n" % (method.upper(), self._get_url(uri))
        response = getattr(self.client, method)(self._get_url(uri), **kwargs)
        try:
            if response.status_code != 200:
                raise Exception("%d: %s" % (
                                 response.status_code,
                                 response.json['error']['message'])
                               )
        except TypeError:
            raise Exception(
              "%d: No Error information supplied by the server" % (
              response.status_code,)
            )

        return response.json

    def get(self, uri, **kwargs):
        return self._response_as_json("get", uri, **kwargs)

    def post(self, uri, data={}, **kwargs):
        return self._response_as_json("post", uri, data=data, **kwargs)

    def put(self, uri, **kwargs):
        return self._response_as_json("put", uri, **kwargs)

    def delete(self, uri, **kwargs):
        return self._response_as_json("delete", uri, **kwargs)
