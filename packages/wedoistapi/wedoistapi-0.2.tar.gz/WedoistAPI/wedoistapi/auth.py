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

from .handler import WedoistRequest

class WedoistAuth (object):
    """
        The base authentication class. This should be subclassed with 
        the methods overridden to provide authentication functionality
        for the API.

        Arguments:
            email: The email address of the user being authenticated.
            password: The password of the user being authenticated.
            uri: The target uri of the login.
    """
    def __init__(self, email, password, uri):
        self.email = email
        self.password = password
        self.uri = uri

    def do_auth(self):
        pass

    def get_cookies(self):
        pass 

    def get_user_data(self):
        pass


class WedoistHTTPAuth (WedoistAuth):
    """
        A basic HTTP auth implementation using urllib2 from the python 
        standard library.

        Arguments:
            email: The email address of the user being authenticated.
            password: The password of the user being authenticated.
            uri: The target uri of the login. (optional)
    """
    def __init__(self, email, password, uri="https://wedoist.com/API/Users/login"):
        WedoistAuth.__init__(self, email, password, uri)
        self.user_data = None
        self.cookies = None

    def do_auth(self):
        post_data = {'email': self.email, 'password': self.password}
        auth_request = WedoistRequest(self.uri)
        auth_response = auth_request.do_request(post_data)
        self.cookies = auth_response.get_cookies()
        self.user_data = auth_response.get_data()
        
    def get_cookies(self):
        return self.cookies

    def get_user_data(self):
        return self.user_data

