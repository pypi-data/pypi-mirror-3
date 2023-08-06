import datetime
import logging
import urllib
import urllib2
import urlparse

__all__ = ('Request', 'HttpServiceAgent', 'LoggingHttpServiceAgent')


class Request(urllib2.Request):
    """
    Extended urllib2 request that allows the request method to be specified.
    """
    def __init__(self, url, data=None, headers=None, method=None, **kwargs):
        if not headers:
            headers = {}
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

    Will not raise HTTPError exceptions. URLError exceptions are still raised
    once they have been logged.
    """
    request_timeout = 30
    enable_proxy_handler = True

    def __init__(self, request_timeout=30, disable_proxy=False, user_agent=None):
        if request_timeout != self.request_timeout:
            self.request_timeout = request_timeout
        if disable_proxy:
            self.enable_proxy_handler = False
        self.user_agent = user_agent

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
        Own version of build opener, does not include unwanted handlers like
        FileOpener, HTTPRedirectHandler, FTPHandler as that usually means
        something to an API.
        """
        import types

        def isclass(obj):
            return isinstance(obj, types.ClassType) or \
                   hasattr(obj, "__bases__")

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
        request = Request(uri, data=data, headers=headers, method=method)

        if self.user_agent:
            request.add_header('User-Agent', self.user_agent)

        return request

    def create_post_request(self, uri, data=None, headers=None):
        """
        Create a HTTP POST request, will handle encoding of data.

        `data` should be a dictionary of key/value pairs.
        """
        query = urllib.urlencode(data) if data else ''
        return self.create_request(uri, query, headers, method='POST')

    def create_get_request(self, uri, data=None, headers=None):
        """
        Create a HTTP GET request, will handle encoding of data to be appended
        to the URI.

        `data` should be a dictionary of key/value pairs.
        """
        if data:
            (scheme, netloc, path, query, fragment) = urlparse.urlsplit(uri)
            if query:
                query += '&' + urllib.urlencode(data)
            else:
                query = urllib.urlencode(data)
            uri = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
        return self.create_request(uri, headers=headers, method='GET')

    def on_send(self, request):
        """
        Event that is raised when a request is about to be sent.

        `request` is a Request object.

        This method can be used to measure request time.
        """

    def on_response(self, request, error=None):
        """
        Event that is raised after a request has been completed. This method is
        called prior to the on_error method if an error is raised. This is can
        be used to measure request time.

        `request` is a Request object.
        `error` is an exception object, in most cases this will be a
            urllib2.URLError exception.

        The error value will only be present if an error is raised.
        """

    def on_error(self, error, request):
        """
        Handler for logging error events.

        `error` is an exception object, in most cases this will be a
            urllib2.URLError exception.
        `request` is the request that caused the error to be raised.

        Returning True from this method prevents he error from being re-raised.
        """

    def on_complete(self, request):
        """
        Event that is raised after a request has been completed. This event is
        raised even if an error occurs and can be used to cleanup.
        """

    def open_request(self, request, timeout=None):
        """
        Open request, can pass in either a request object or a plain URI.
        """
        if not isinstance(request, Request):
            request = self.create_request(request)

        opener = self._build_opener()

        self.on_send(request)
        try:
            response = opener.open(request, timeout=self.request_timeout)
        except urllib2.URLError, uex:
            self.on_response(request, uex)
            if not self.on_error(uex, request):
                raise
        else:
            self.on_response(request)
            return response
        finally:
            self.on_complete(request)


class LoggingHttpServiceAgent(HttpServiceAgent):
    """
    Adds logging support to Service Agent
    """
    def __init__(self, logger=None, *args, **kwargs):
        super(LoggingHttpServiceAgent, self).__init__(*args, **kwargs)
        self._logger = logger if logger else logging.getLogger(self.__class__.__module__ + self.__class__.__name__)

    def on_send(self, request):
        request.start = datetime.datetime.now()
        self._logger.debug('Sending %s request to: %s', request.get_method(), request.get_full_url())

    def on_response(self, request, error=None):
        request.end = datetime.datetime.now()
        duration = request.end - request.start
        request.duration = duration.total_seconds()
        if error:
            self._logger.debug('Response in %fs with errors.', request.duration)
        else:
            self._logger.debug('Response in %fs.', request.duration)

    def on_error(self, error, request):
        self._logger.error(error)

    def on_complete(self, request):
        self._logger.debug('Completed request for: %s', request.get_full_url())
