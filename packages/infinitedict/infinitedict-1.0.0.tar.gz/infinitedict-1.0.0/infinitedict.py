from collections import defaultdict

VERSION = (1, 0, 0)
__version__ = '.'.join(map(str, VERSION))

class InfiniteDict(defaultdict):
    """
    An infinitely and automatically nesting dictionary
    with default leaf attributes.
    
    e.g.
    >>> d = InfiniteDict(count=0)
    >>> d['abc']['xyz'].count += 123
    >>> print d['abc']['xyz'].count
    123
    """
    def __init__(self, **kargs):
        self._kargs = kargs
        defaultdict.__init__(self, self._get_func)
        for k,v in kargs.iteritems():
            if hasattr(self.__dict__, k):
                # Don't override built-in attributes.
                continue
            self.__dict__[k] = (v() if callable(v) else v)
    def _get_func(self):
        return self.__class__(**self._kargs)

if __name__ == '__main__':
    
    d = InfiniteDict(val1=list, val2=0)
    #d['abc'].value = 123
    #d['abc']['def'].value = 456
    #print d['abc']
    #print d['abc']['def']
    print 'test:'
    print 'list:',d['abc'].val1
    d['abc'].val1.append(123)
    print 'list:',d['abc'].val1
    print 'list:',d['abc']['def'].val1
    print 'int:',d['abc']['def'].val2
    d.somerandomvalue = 'somerandomvalue'
    print d.somerandomvalue
    