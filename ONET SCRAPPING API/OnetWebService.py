import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import base64
import json

'''
Class which is responsible for establishing the connection with ONET api and retrive the data
'''
class OnetWebService:
    '''
    Constructor which uses the credentials from the config.ini in util to establish connection with API
    '''
    def __init__(self, username, password):
        self._headers = {
            'User-Agent': 'python-OnetWebService/1.00 (bot)',
            'Authorization': 'Basic ' + base64.standard_b64encode((username + ':' + password).encode()).decode(),
            'Accept': 'application/json' }
        self.set_version()

    '''
    Setting up the base url
    '''
    def set_version(self, version = None):
        if version is None:
            self._url_root = 'https://services.onetcenter.org/ws/'
        else:
            self._url_root = 'https://services.onetcenter.org/v' + version + '/ws/'

    def call(self, path, *query):
        url = self._url_root + path #based one the path provided it will either call base API or miliarty API
        if len(query) > 0:
            url = urllib.parse.unquote(url+"/".join(query))
        req = urllib.request.Request(url, None, self._headers)
        handle = None
        try:
            handle = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            if e.code == 422:
                return json.load(e)
            else:
                return { 'error': 'Call to ' + url + ' failed with error code ' + str(e.code) }
        except urllib.error.URLError as e:
            return { 'error': 'Call to ' + url + ' failed with reason: ' + str(e.reason) }
        code = handle.getcode()
        if (code != 200) and (code != 422):
            return { 'error': 'Call to ' + url + ' failed with error code ' + str(code),
                     'urllib2_info': handle }
        return json.load(handle)
