import hmac
import json
import base64
import urllib
import hashlib

class ApiKeySession(object):
    def __init__(self):
        pass

    def open(self, api, kwargs):
        required = ('apikey',
                    'secretkey')
        if not all(x in kwargs.keys() for x in required):
            raise SyntaxError("The selected authentication method "
                              "requires an apikey and a secretkey")
        self.apikey = kwargs['apikey']
        self.secretkey = kwargs['secretkey']
        self.api_url = api.api_url

    def do_request(self, command, args):
        return self._make_request(command, args)

    def _http_get(self, url):
        response = urllib.urlopen(url)
        return response.read()

    def _make_request(self, command, args):
        args['response'] = 'json'
        args['command'] = command
        self.request(args)
        #print self.value
        data = self._http_get(self.value)
        # The response is of the format {commandresponse: actual-data}
        key = command.lower() + "response"
        return json.loads(data)[key]

    def request(self, args):
        args['apiKey'] = self.apikey

        self.params = []
        self._sort_request(args)
        self._create_signature()
        self._build_post_request()

    def _sort_request(self, args):
        keys = sorted(args.keys())

        for key in keys:
            self.params.append(key + '=' + urllib.quote_plus(args[key]))

    def _create_signature(self):
        self.query = '&'.join(self.params)
        digest = hmac.new(
            self.secretkey,
            msg=self.query.lower(),
            digestmod=hashlib.sha1).digest()
        self.signature = base64.b64encode(digest)

    def _build_post_request(self):
        self.query += '&signature=' + urllib.quote_plus(self.signature)
        self.value = self.api_url + '?' + self.query
