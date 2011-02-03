import urlparse
import httplib2
try:
    import json
except ImportError:
    import simplejson as json

from pinder.exc import HTTPUnauthorizedException, HTTPNotFoundException
from pinder.multipart import encode_multipart, BOUNDARY


class HTTPConnector(object):
    """Makes the actual connection to the server and handles the response"""
    def __init__(self, subdomain, token, ssl=False, ua=''):
        # The User agent of the client
        self.user_agent = ua
        schema = ('http', 'https')[ssl==True]
        # The URI object of the Campfire account.
        self.uri = urlparse.urlparse(
            "%s://%s.campfirenow.com" % (schema, subdomain))
        self._http = httplib2.Http(timeout=5)
        self._http.force_exception_to_status_code = True
        self._http.add_credentials(token, 'X')

    def get(self, path='', data=None, headers=None):
        return self._request('GET', path, data, headers)

    def post(self, path, data=None, headers=None, file_upload=False):
        return self._request('POST', path, data, headers, file_upload)

    def put(self, path, data=None, headers=None):
        return self._request('PUT', path, data, headers)

    def delete(self, path):
        return self._request('DELETE', path)
        
    def get_credentials(self):
        credentials = list(self._http.credentials.iter(''))
        if credentials:
            return credentials[0]

    def _uri_for(self, path=''):
        return "%s/%s.json" % (urlparse.urlunparse(self.uri), path)

    def _request(self, method, path, data=None, additional_headers=None, file_upload=False):
        additional_headers = additional_headers or dict()
        data = data or dict()
        
        headers = {}
        headers['user-agent'] = self.user_agent

        if method.upper() ==  'POST' and file_upload:
            data = encode_multipart(BOUNDARY, data)
            headers['content-type'] = 'multipart/form-data; boundary=%s' % BOUNDARY
        else:
            data = json.dumps(data)
            headers['content-type'] = 'application/json'
        
        headers['content-length'] = str(len(data))
        headers.update(additional_headers)

        if method in ('GET', 'POST', 'PUT', 'DELETE'):
            location = self._uri_for(path)
        else:
            raise Exception('Unsupported HTTP method: %s' % method)

        response, body = self._http.request(location, method, data, headers)

        if response.status == 401:
            raise HTTPUnauthorizedException(
                "You are not authorized to access the resource: '%s'" % path)
        elif response.status == 404:
            raise HTTPNotFoundException(
                "The resource you are looking for does not exist (%s)" % path)

        try:
            return json.loads(body)
        except ValueError, e:
            if response.status not in (200, 201):
                raise Exception("Something did not work fine: HTTP %s - %s - %s" % (
                    response.status, str(e), body))
