"""
Copyright (C) 2012 <Wedoist>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

try:
    import json
except ImportError:
    import simplejson as json

import cookielib
from urllib2 import Request, urlopen
from urllib import urlencode


class WedoistRequest (object):
    """
        A very basic http request using urllib2 from the standard
        library.

        This can be subclassed for other types of requests provided
        the subclass implements the do_request method and returns an
        appropriate WedoistResponse or subclass thereof.

        Arguments:
            uri: The URI of the request.

    """
    def __init__(self, uri):
        self.uri = uri
        
    def do_request(self, post_data=None, session_cookies=None):
        """
            Called to execute the request.

            Arguments:
                post_data: Any POST data that needs to be sent with the 
                    request.
                session_cookies: Any cookies/headers that need to be sent
                    with the request.

            Error handling:
                The request throws HTTPError on failure. Check the urllib2 
                documentation for more information.
        """
        ## Build the request
        request = Request(self.uri, urlencode(post_data))
        ## If we have session cookies, add them to the header
        if session_cookies:
            session_cookies.add_cookie_header(request)
        ## Make the request
        response = urlopen(request)
        ## Get the cookies if any out of the header of the response
        cookies = cookielib.CookieJar()
        cookies.extract_cookies(response,request)
        ## Return a WedoistResponse or subclass with the raw data and
        ## any cookies.
        return WedoistResponse(response.read(), cookies)


class WedoistResponse (object):
    """
        A very basic HTTP response that decodes the JSON data.
    """
    def __init__(self, data, cookies):
        #print "Response:"
        #print "  data: ", data
        #print "  cookies: ", cookies
        self._data = data
        self._cookies = cookies

    def get_data(self):
        """
            Return the final decoded data.
        """
        ## TODO remove
        return json.loads(self._data)

    def get_cookies(self):
        """ 
            Return any cookies supplied by the headers of the request
        """
        return self._cookies

