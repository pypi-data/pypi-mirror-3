### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
from persistent import Persistent

# import Zope3 interfaces

# import local interfaces
from ztfy.cache.interfaces import ICacheHandler, IPersistentCacheProxyHandler
from ztfy.cache.metadirectives import ICacheProxyHandler

# import Zope3 packages
from zope.component import queryUtility
from zope.container.contained import Contained
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages


class CacheProxyHandler(object):
    """Cache proxy handler"""

    implements(ICacheProxyHandler)

    name = FieldProperty(ICacheProxyHandler['name'])
    cache_interface = FieldProperty(ICacheProxyHandler['cache_interface'])
    cache_name = FieldProperty(ICacheProxyHandler['cache_name'])

    def __init__(self, name, cache_interface, cache_name):
        self.name = name
        self.cache_interface = cache_interface
        self.cache_name = cache_name

    def getCache(self):
        return ICacheHandler(queryUtility(self.cache_interface, self.cache_name), None)


class PersistentCacheProxyHandler(Persistent, Contained):
    """Persistent cache proxy handler"""

    implements(IPersistentCacheProxyHandler)

    cache_interface = FieldProperty(IPersistentCacheProxyHandler['cache_interface'])
    cache_name = FieldProperty(IPersistentCacheProxyHandler['cache_name'])

    def getCache(self):
        return ICacheHandler(queryUtility(self.cache_interface, self.cache_name), None)
