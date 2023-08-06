from pyramid.security import Allow
from pyramid.security import Everyone

from . import tables

import logging
log = logging.getLogger(__name__)

class Locatable(object):
    __name__ = None
    __parent__ = None
    def __init__(self, *args, **kwargs):
        self.__name__ = kwargs.get('name', None)
        self.__parent__ = kwargs.get('parent', None)

class IntKeyTraverser(object):
    def __getitem__(self, key):
        session = tables.DBSession
        try:
            key = int(key)
        except (ValueError, TypeError):
            raise KeyError(key)
        item = session.query(self.__model__).get(key)
        if item is None:
            raise KeyError(key)
        item.__parent__ = self
        item.__name__ = unicode(key)
        return item

class ExtensionTraverser(IntKeyTraverser):
    def __getitem__(self, key):
        if key.endswith(self.__extension__):
            key = key[0:-len(self.__extension__)]
        return IntKeyTraverser.__getitem__(self, key)

class Shards(ExtensionTraverser, Locatable):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:admin', 'post') ]
    __model__ = tables.Shard
    __extension__ = '.png'

class Shows(ExtensionTraverser, Locatable):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:admin', 'post') ]
    __model__ = tables.Slideshow
    __extension__ = '.rss'

class Sharder(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:admin', 'post') ]
    __name__ = ''
    __parent__ = None
    __children__ = {'shards':Shards, 'shows':Shows} 
    
    def __getitem__(self, key):
        return self.__children__[key](name=key, parent=self)
    
def make():
    root = Sharder()
    def get_root(request):
        return root
    return get_root
