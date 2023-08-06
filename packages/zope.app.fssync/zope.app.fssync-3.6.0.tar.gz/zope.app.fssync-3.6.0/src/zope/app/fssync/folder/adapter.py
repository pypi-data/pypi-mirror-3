##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Filesystem synchronization support.

$Id: adapter.py 76675 2007-06-14 07:05:37Z oestermeier $
"""
__docformat__ = 'restructuredtext'


from zope import interface
from zope import component
from zope.fssync import synchronizer
from zope.fssync import interfaces

from zope.app.component.interfaces import ISite
from zope.app.component.site import LocalSiteManager


class FolderSynchronizer(synchronizer.DirectorySynchronizer):
    """Adapter to provide an fssync serialization of folders
    """
 
    interface.implements(interfaces.IDirectorySynchronizer)
    
    def iteritems(self):
        """Compute a folder listing.

        A folder listing is a list of the items in the folder.  It is
        a combination of the folder contents and the site-manager, if
        a folder is a site.

        The adapter will take any mapping:
        
        >>> adapter = FolderSynchronizer({'x': 1, 'y': 2})
        >>> len(list(adapter.iteritems()))
        2
        
        If a folder is a site, then we'll get ++etc++site included.

        >>> import zope.interface
        >>> class SiteManager(dict):
        ...     pass
        >>> class Site(dict):
        ...     zope.interface.implements(ISite)
        ...
        ...     def getSiteManager(self):
        ...         return SiteManager()
        
        >>> adapter = FolderSynchronizer(Site({'x': 1, 'y': 2}))
        >>> len(list(adapter.iteritems()))
        3


        """
        for key, value in self.context.items():
            yield (key, value)
     
        if ISite.providedBy(self.context):
            sm = self.context.getSiteManager()
            yield ('++etc++site', sm)

    def __setitem__(self, key, value):
        """Sets a folder item.
        
        Note that the ++etc++site key can also be handled 
        by the LocalSiteManagerGenerator below.

        >>> from zope.app.folder import Folder
        >>> folder = Folder()
        >>> adapter = FolderSynchronizer(folder)
        >>> adapter[u'test'] = 42
        >>> folder[u'test']
        42
        
        Since non-unicode names must be 7bit-ascii we try
        to convert them to unicode first:
        
        >>> adapter['t\xc3\xa4st'] = 43
        >>> adapter[u't\xe4st']
        43
        
        """
        if key == '++etc++site':
            self.context.setSiteManager(value)
        else:
            if not isinstance(key, unicode):
                key = unicode(key, encoding='utf-8')
            self.context[key] = value


class LocalSiteManagerGenerator(object):
    """A generator for a LocalSiteManager.
    
    A LocalSiteManager has a special __init__ method.
    Therefore we must provide a create method.
    """
    interface.implements(interfaces.IObjectGenerator)
    
    def create(self, context, name):
        """Creates a sitemanager in the given context."""
        sm = LocalSiteManager(context)
        context.setSiteManager(sm)
        return sm


