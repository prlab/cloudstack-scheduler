import json
import pprint
import urllib
import urllib2
import hashlib

class UsernameSession(object):
    def __init__(self):
        pass

    def open(self, api, kwargs):
        required = ('username',
                    'password')
        if not all(x in kwargs.keys() for x in required):
            raise SyntaxError("The selected authentication method "
                              "requires a username and a password")
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.api_url = api.api_url
        self.__int_init(url=self.api_url, username=self.username, password=self.password)

    def do_request(self,name,kwargs):
        if kwargs:
            kwargs.update({'command': name})
            return self.request(kwargs)
        else:
            return self.request({'command': name})

    def __int_init(self, url='', username=None, password=None, domain=None, logging=False):

        self.username = username
        self.password = password #hashlib.md5(password).hexdigest()
        self.sessionkey = None
        self.domainid = None
        self.type = None
        self.userid = None
        self.errors = []
        self.logging = logging

        # setup cookie handling
        self.caller = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.caller)

        # login so you can get a sessionkey (and a cookie)
        login_query = dict()
        login_query['command'] = 'login'
        login_query['username'] = self.username
        login_query['password'] = self.password
        if domain:
            login_query['domain'] = domain

        login_result = self.request(login_query)
        if login_result:
            self.sessionkey = login_result['sessionkey']
            self.domainid = login_result['domainid']
            self.type = login_result['type']
            self.userid = login_result['userid']
        else:
            self.errors.append("Login failed...")
            print self.errors

    def request(self, params):
        """Builds a query from params and return a json object of the result or None"""
        if self.sessionkey or (self.username and self.password and params['command'] == 'login'):
            # add the default and dynamic params
            params['response'] = 'json'

            if self.sessionkey:
                params['sessionkey'] = self.sessionkey

            # build the query string
            query_params = map(lambda (k,v):k+"="+urllib.quote(str(v)), params.items())
            query_string = "&".join(query_params)

            # final query string...
            url = self.api_url+"?"+query_string

            output = None
            try:
                output = json.loads(self.caller.open(url).read())
            except urllib2.HTTPError, e:
                self.errors.append("HTTPError: "+str(e.code))
            except urllib2.URLError, e:
                self.errors.append("URLError: "+str(e.reason))

            if output:
                output = output[(params['command']).lower()+'response']

            if self.logging:
                with open('request.log', 'a') as f:
                    f.write('request:\n')
                    f.write(url)
                    f.write('\n\n')
                    f.write('response:\n')
                    if output:
                        pprint.pprint(output, f, 2)
                    else:
                        f.write(repr(self.errors))
                    f.write('\n\n\n\n')

            return output
        else:
            self.errors.append("missing credentials in the constructor")
            return None
