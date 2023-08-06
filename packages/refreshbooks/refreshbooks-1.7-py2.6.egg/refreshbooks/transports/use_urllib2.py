import urllib2 as u

from refreshbooks import exceptions as exc

class Transport(object):
    def __init__(self, url, headers_factory):
        self.url = url
        self.headers_factory = headers_factory
    
    def __call__(self, entity):
        request = u.Request(
            url=self.url,
            data=entity,
            headers=self.headers_factory()
        )
        try:
            return u.urlopen(request).read()
        except u.HTTPError, e:
            raise exc.TransportException(e.code, e.read())
