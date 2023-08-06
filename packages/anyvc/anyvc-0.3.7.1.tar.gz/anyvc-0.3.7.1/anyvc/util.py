"""
    anyvc.util
    ~~~~~~~~~~

    some utility classes that help with metadata
"""

import logging

def http_code_content(path):
    try:
        import urllib
        res = urllib.urlopen(path)
        return res.code, res.read()
    except Exception as e: # diaper
        logging.error('no data for path %s, error %s', path, e)
        return -1, ''



class cachedproperty(object):
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, type):
        if obj is None:
            return self
        else:
            result = self.func(obj)
            setattr(obj, self.__name__, result)
            return result

