.. contents::

Introduction
============

ZTFY.cache is a small package which provides a common interface to handle several cache backends.

Currently available backends include Zope native RAM cache and Memcached cache.


Cache proxy
===========

The main concept included ZTFY.cache package is just those of a small proxy which provides a same
interfaces to several proxy classes.

When defining a proxy, you just have to set the interface and the registration name matching the
given registered cache utility. Cache access is then bound to the ICacheHandler interface, which
allows you to set, query and invalidate data in the cache.

The cache proxy can be defined as a persistent utility, or through ZCML directives. Using ZCML can
allow you to define different caches, according to the used application front-end.
