'''
Created on 01.06.2009

@author: falko
'''

from rfc822 import formatdate, time

try:
    # the fast way
    import cjson
    _encode = cjson.encode
    jsonDecode = cjson.decode
except ImportError:
    try:
        # the python 2.6 way
        import json
        _encode = json.dumps
        jsonDecode = json.loads
    except ImportError:
        # the slow python < 2.6 way
        import simplejson
        from simplejson import JSONEncoder
        ##encode = simplejson.dumps
        _encode = JSONEncoder(skipkeys=True, ensure_ascii=False).encode 
        jsonDecode = simplejson.loads

from zope.i18n import translate

def translateObject(o, context):
    if isinstance(o, list):
        for index, value in enumerate(o):
            o[index] = translateObject(value, context)
    elif isinstance(o, tuple):
        o = [translateObject(value, context) for value in o]
    elif isinstance(o, dict):
        for key, value in o.items():
            o[key] = translateObject(value, context)
    elif isinstance(o, unicode):
        o = translate(o, context=context)
    return o

def encode(obj, context=None):
    obj = translateObject(obj, context)    
    return _encode(obj)

def setNoCacheHeaders(response):
    """Ensure that the result isn't cached"""
    response.setHeader('Pragma', 'no-cache')
    response.setHeader('Cache-Control', 'no-cache')
    response.setHeader('Expires', formatdate(time.time() - 7 * 86400)) # 7 days ago
    
def jsonmethod(func):
    """ encode result to json format """
    def encode(*args, **kw):
        self = args[0]
        request = getattr(self, 'request', None)
        if request != None:
            request.response.setHeader('Content-Type', 'text/json')
                 
        return encode(func(*args, **kw))

    return encode