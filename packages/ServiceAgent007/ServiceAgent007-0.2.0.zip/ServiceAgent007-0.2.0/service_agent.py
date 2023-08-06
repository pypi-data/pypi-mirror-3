import datetime
import logging
import urllib
import urllib2
import urlparse

class Request(urllib2.Request):
    """
    Extended urllib2 request that allows the request method to be specified.
    """
    def __init__(self, url, data=None, headers=None, method=None, **kwargs):
        if not headers: headers = {}
        urllib2.Request.__init__(self, url, data, headers, **kwargs)
        self.method = method

    def get_method(self):
        if self.method:
            return self.method
        else:
            return urllib2.Request.get_method(self)

class HttpServiceAgent(object):
    """
    Custom wrapper for urllib2 suited for HTTP REST service requests.

    Will not raise HTTPError exceptions. URLError exceptions are still raised once they have been logged.
    """
    request_timeout = 30 # seconds
    enable_proxy_handler = True

    def _get_handlers(self):
        """
        Get collection of default handlers we want to support.
        """
        if not hasattr(self, '__default_classes'):
            import httplib
            default_classes = []

            if self.enable_proxy_handler:
                default_classes.append(urllib2.ProxyHandler)

            default_classes.append(urllib2.HTTPHandler)
            
            if hasattr(httplib, 'HTTPS'):
                default_classes.append(urllib2.HTTPSHandler)

            self.__default_classes = tuple(default_classes)

        return self.__default_classes

    def _build_opener(self):
        """
        Own version of build opener, does not include unwanted handlers like FileOpener, HTTPRedirectHandler,
        FTPHandler as that usually means something to an API.
        """
        import types
        def isclass(obj):
            return isinstance(obj, types.ClassType) or hasattr(obj, "__bases__")

        opener = urllib2.OpenerDirector()
        for h in self._get_handlers():
            if isclass(h):
                h = h()
            opener.add_handler(h)
        return opener

    def create_request(self, uri, data=None, headers=None, method=None):
        """
        Create an HTTP request object.
        """
        return Request(uri, data=data, headers=headers, method=method)

    def create_post_request(self, uri, data=None, headers=None):
        """
        Create a HTTP POST request, will handle encoding of data.

        `data` should be a dictionary of key/value pairs.
        """
        query = urllib.urlencode(data) if data else ''
        return Request(uri, data=query, headers=headers, method='POST')

    def create_get_request(self, uri, data=None, headers=None):
        """
        Create a HTTP GET request, will handle encoding of data to be appended to the URI.

        `data` should be a dictionary of key/value pairs.
        """
        if data:
            (scheme, netloc, path, query, fragment) = urlparse.urlsplit(uri)
            if query:
                query += '&' + urllib.urlencode(data)
            else:
                query = urllib.urlencode(data)
            uri = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
        return Request(uri, headers=headers, method='GET')

    def pre_open_request(self, request):
        """
        Event that is raised prior to opening a request.

        `request` is a Request object.
        """
        pass

    def post_open_request(self, request, error=None):
        """
        Event that is raised after a request has been completed. This method is called prior to the
        handle_open_request_error method if an error is raised. This is can be used to log request length.

        `request` is a Request object.
        `error` is a urllib2.URLError exception object.
        """
        pass

    def handle_open_request_error(self, error, request):
        """
        Handler for logging error events.

        `error` is a urllib2.URLError exception object.
        `request` is the request that caused the error to be raised.

        Returning True from this method prevents he error from being re-raised.
        """
        pass

    def open_request(self, request):
        """
        Open request, can pass in either a request object or a plain URI.
        """
        if not isinstance(request, Request):
            request = self.create_request(request)

        opener = self._build_opener()

        self.pre_open_request(request)
        try:
            result = opener.open(request, timeout=self.request_timeout)
        except urllib2.URLError, uex:
            self.post_open_request(request, uex)
            if not self.handle_open_request_error(uex, request):
                raise
        else:
            self.post_open_request(request)
            return result

class LoggingHttpServiceAgent(HttpServiceAgent):
    """
    Adds logging support to our Service Agent
    """
    logger = logging.Logger(__name__)

    def pre_open_request(self, request):
        request.start = datetime.datetime.now()
        self.logger.debug('Making %s request to: %s', request.get_method(), request.get_full_url())

    def post_open_request(self, request, error=None):
        end = datetime.datetime.now()
        duration = end - request.start
        if error:
            self.logger.debug('Request completed in %fs with errors.', duration.total_seconds())
        else:
            self.logger.debug('Request completed in %fs.', duration.total_seconds())

    def handle_open_request_error(self, error, request):
        self.logger.error(error)


if __name__ == '__main__':
    class CustomServiceAgent(LoggingHttpServiceAgent):
        request_timeout = 10 # Override request timeout to 10 seconds
        pass

    agent = CustomServiceAgent()
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    agent.logger.addHandler(ch)

    r = agent.open_request('http://www.google.com')
    print r.code

    r = agent.open_request('http://made.up.example.com')
    r = agent.open_request(agent.create_request('http://made.up.example.com'))

    r = agent.open_request('http://bender.poweredbypenguins.org:443/')
    r = agent.open_request('http://localhost:80/')
    print r
