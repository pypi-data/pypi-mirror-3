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
"""Filesystem synchronization functions.

$Id: syncer.py 97912 2009-03-11 20:04:22Z amos $
"""
__docformat__ = 'restructuredtext'

import tempfile

from zope import interface
from zope import component
from zope import proxy
from zope.security.management import checkPermission
from zope.security.checker import ProxyFactory

from zope.fssync import synchronizer
from zope.fssync import task
from zope.fssync import repository
from zope.fssync import interfaces
from zope.fssync import pickle


def getSynchronizer(obj, raise_error=True):
    """Returns a synchronizer.

    Looks for a named factory first and returns a default serializer
    if the dotted class name is not known.

    Checks also for the permission to call the factory in the context 
    of the given object.

    Removes the security proxy for the adapted object 
    if a call is allowed and adds a security proxy to the
    synchronizer instead.
    """
    dn = synchronizer.dottedname(obj.__class__)    

    factory = component.queryUtility(interfaces.ISynchronizerFactory, name=dn)
    if factory is None:
        factory = component.queryUtility(interfaces.ISynchronizerFactory)
    if factory is None:
        if raise_error:
            raise synchronizer.MissingSynchronizer(dn)
        return None    

    checker = getattr(factory, '__Security_checker__', None)
    if checker is None:
        return factory(obj)
    permission = checker.get_permissions['__call__']
    if checkPermission(permission, obj):
        return ProxyFactory(factory(proxy.removeAllProxies(obj)))


def toFS(obj, name, location):
    filesystem = repository.FileSystemRepository()
    checkout = task.Checkout(getSynchronizer, filesystem)
    return checkout.perform(obj, name, location)

def toSNARF(obj, name):
    temp = tempfile.TemporaryFile()
    # TODO: Since we do not know anything about the target system here,
    # we try to be on the save side. Case-sensivity and NFD should be 
    # determined from the request.
    
    snarf = repository.SnarfRepository(temp, case_insensitive=True, enforce_nfd=True)
    checkout = task.Checkout(getSynchronizer, snarf)
    checkout.perform(obj, name)
    return temp

