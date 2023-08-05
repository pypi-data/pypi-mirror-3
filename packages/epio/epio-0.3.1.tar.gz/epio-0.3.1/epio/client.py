import getpass
import os
import sys
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha
try:
    import json
except ImportError:
    import simplejson as json
import httplib2
import urlparse
from urllib import urlencode
import epio

class AuthError(Exception):
    pass

class AuthenticationSucceeded(Exception):
    pass

class EpioClient(object):
    """
    A client for the ep.io API.
    """
    def __init__(self, token_file, email=None, password=None):
        self._token_file = token_file
        self.email = email
        self.password = password
        # Make the Http instance (optionally with proxy info)
        proxy_info = None
        proxy_url = os.environ.get('HTTP_PROXY', os.environ.get("http_proxy", None))
        if proxy_url:
            scheme, netloc, path, parameters, query, fragment = urlparse.urlparse(proxy_url)
            if scheme != "http":
                print "Unsupported proxy url: %s" % proxy_url
                sys.exit(1)
            if ":" in netloc:
                host, port = netloc.split(":", 1)
            else:
                host = netloc
                port = 80
            proxy_info = httplib2.ProxyInfo(3, host, port)
        try:
            self.http_client = httplib2.Http(
                proxy_info=proxy_info,
                ca_certs=os.path.join(
                    os.path.dirname(__file__), "ssl", "StartCom_CA.pem"
                ),
            )
        except TypeError:
            # Older httplib versions
            self.http_client = httplib2.Http(
                proxy_info=proxy_info,
            )
        self.access_token = None
        try:
            self.access_token = self.read_token_file()
        except (IOError, KeyError):
            self.authenticate_from_stdin()

    @property
    def token_file(self):
        return os.path.expanduser(self._token_file) + "_" + sha(
            self.get_host() + "||" + (self.email or "no-email")
        ).hexdigest()[:8]
    
    def read_token_file(self):
        """
        Reads a token from disk.
        """
        return open(self.token_file).read().strip()
    
    def write_token_file(self):
        """
        Writes our token out to disk.
        """
        try:
            os.makedirs(os.path.dirname(self.token_file))
        except OSError:
            pass
        return open(self.token_file, "w").write(self.access_token)
    
    def authenticate_from_stdin(self):
        """
        Prompt for email and password at the command line and authenticate with
        them.
        """
        email = self.email
        if email is None:
            print "Enter your ep.io login details"
            email = raw_input('Email: ')
        password = self.password
        if password is None:
            password = getpass.getpass('Password: ')
        self.authenticate(email, password)
    
    def authenticate(self, email, password):
        """
        Authenticate with epio API given an email and password and save the 
        access token on success.
        """
        try:
            response, content = self.request(
                path = 'token/',
                method = 'POST',
                headers = {
                    "X-Epio-Email": email,
                    "X-Epio-Password": password,
                },
            )
        except AuthenticationSucceeded:
            # They tried again and succeeded down the stack
            return 

        if response.status != 200:
            if response.status == 401:
                raise AuthError(content)
            else:
                raise AuthError('Unknown authentication error (%s): %s' % (
                    response.status,
                    content,
                ))
        self.access_token = content
        
        # Save new token to disk
        self.write_token_file()
    
    def get(self, path):
        return self.request(path, 'GET')
    
    def post(self, path, data):
        return self.request(path, 'POST', data)
    
    def put(self, path, data):
        return self.request(path, 'PUT', data)
    
    def delete(self, path):
        return self.request(path, 'DELETE')
    
    def request(self, path, method='GET', data=None, headers=None):
        """
        Make a request to the API.
        """
        # Get the actual URL
        url = self.get_url(path)
        # Work out the right headers
        if headers is None:
            headers = {}
        headers["Accept"] = "application/json"
        if self.access_token:
            headers["X-Epio-Token"] = self.access_token
        if data is not None:
            headers['Content-type'] = 'application/x-www-form-urlencoded'
        # Send the request.
        try:
            response, content = self.http_client.request(
                url,
                method,
                headers = headers,
                body = data and urlencode(data) or "",
            )
        except AttributeError:
            print "Could not open connection to %s" % url
            if url.startswith("https"):
                print "You can try without using SSL by setting the environment variable EPIO_NO_HTTPS to 1."
            sys.exit(1)
        if response.status not in (404, 302, 503, 504) and content:
            try:
                content = json.loads(content)
            except ValueError:
                print "Error: non-JSON response. This is probably a problem with the ep.io service."
                if os.environ.get("EPIO_DEBUG", False):
                    print content
                sys.exit(1)
        elif response.status in (503, 504):
            print "Error: ep.io appears to be down. Please try again in a short while."
            if os.environ.get("EPIO_DEBUG", False):
                print content
            sys.exit(1)
        else:
            content = None
        # Reauthenticate
        # FIXME: Make the logic here more sane.
        if response.status == 401:
            print "Authentication Error: %s\n" % content['message']
            self.authenticate_from_stdin()
            if path == "token/":
                raise AuthenticationSucceeded()
            else:
                return self.request(path, method, data)

        return response, content
    
    def get_url(self, path):
        """
        Returns the full URL given an API path.
        """
        if os.environ.get("EPIO_NO_HTTPS", False):
            protocol = "http"
        else:
            protocol = "https"
        if path[0] == "/":
            return '%s://%s%s' % (
                protocol,
                self.get_host(),
                path
            )
        else:
            return '%s://%s/control/%s' % (
                protocol,
                self.get_host(),
                path
            )

    def get_host(self):
        return os.environ.get('EPIO_HOST', 'www.ep.io')
    

