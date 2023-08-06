from .utils import curry

class Channel(object):
    API_ENDPOINT = 'http://api.pushscreen.io'
    
    def __init__(self, name):
        self.name = name
    
    def push(self, type, **kwargs):
        import requests
        payload = dict(type=type, **kwargs)
        r = requests.post('%s/%s' % (self.API_ENDPOINT, self.name), data=payload)
        return r.json
    
    def url(self, url, **kwargs):
        return self.push(type='url', url=url, **kwargs)
    
    def html(self, html, **kwargs):
        return self.push(type='html', html=html, **kwargs)
    
    def clear(self, **kwargs):
        return self.push(type='clear', **kwargs)
