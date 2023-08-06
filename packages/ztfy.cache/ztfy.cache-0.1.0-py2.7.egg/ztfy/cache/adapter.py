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

# import Zope3 interfaces
from lovely.memcached.interfaces import IMemcachedClient
from zope.ramcache.interfaces.ram import IRAMCache

# import local interfaces
from ztfy.cache.interfaces import ICacheHandler

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements

# import local packages


class RAMCacheAdapter(object):
    """RAM cache adapter"""

    adapts(IRAMCache)
    implements(ICacheHandler)

    def __init__(self, context):
        self.context = context

    def set(self, namespace, key, value):
        if not isinstance(key, dict):
            key = { '_key': key }
        self.context.set(value, namespace, key)

    def query(self, namespace, key, default=None):
        if not isinstance(key, dict):
            key = { '_key': key }
        return self.context.query(namespace, key, default)

    def invalidate(self, namespace, key=None):
        if (key is not None) and not isinstance(key, dict):
            key = { '_key': key }
        self.context.invalidate(namespace, key)

    def invalidateAll(self):
        self.context.invalidateAll()


class MemcachedCacheAdapter(object):
    """Memcached cache adapter"""

    adapts(IMemcachedClient)
    implements(ICacheHandler)

    def __init__(self, context):
        self.context = context

    def set(self, namespace, key, value):
        self.context.set(value, key, ns=namespace)

    def query(self, namespace, key, default=None):
        return self.context.query(key, default, ns=namespace)

    def invalidate(self, namespace, key=None):
        self.context.invalidate(key, ns=namespace)

    def invalidateAll(self):
        self.context.invalidateAll()
