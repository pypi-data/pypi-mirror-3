import sys
if sys.version_info[:2] >= (3,0):
    import urllib.request as urllib2
    from urllib.parse import urlencode
else:
    import urllib2
    from urllib import urlencode
import json
from version import __version__

class Data(object):
    url = 'http://api.hastests.com/data'
    headers = {'User-Agent': 'hastests-python '+__version__}

    def __init__(self, script):
        self.data = urlencode({'q': script})

    def generate(self, seed=None):
        s = seed and '&'+urlencode({'seed': seed}) or ''
        req = urllib2.Request(Data.url+'?'+self.data+s, None, Data.headers)
        return json.loads(urllib2.urlopen(req).read().decode('utf-8'))
