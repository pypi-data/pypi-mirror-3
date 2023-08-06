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

# import local interfaces

# import Zope3 packages
from zope.configuration.fields import GlobalInterface
from zope.interface import Interface
from zope.schema import TextLine

# import local packages

from ztfy.cache import _


class ICacheProxyHandlerBase(Interface):
    """Cache proxy handler base interface"""

    def getCache(self):
        """Get the real cache utility"""


class ICacheProxyHandlerInfo(Interface):
    """A cache handler is a proxy to an actual cache utility"""

    name = TextLine(title=_("Cache handler name"),
                    required=False)

    cache_interface = GlobalInterface(title=_("Cache utility interface"),
                                      required=True)

    cache_name = TextLine(title=_("Cache utility name"),
                          required=False)


class ICacheProxyHandler(ICacheProxyHandlerBase, ICacheProxyHandlerInfo):
    """Cache proxy handler interface"""
