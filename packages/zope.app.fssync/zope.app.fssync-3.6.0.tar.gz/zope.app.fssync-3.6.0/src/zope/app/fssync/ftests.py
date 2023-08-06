##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Functional fssync tests

$Id: ftests.py 40495 2005-12-02 17:51:22Z efge $
"""
import re
import unittest
import os
import shutil
import time
import tempfile
import sys
import zope
from zope.testing import renormalizing, doctest, module, doctestunit
from zope.app.testing import functional
from zope.testbrowser.testing import PublisherConnection

from zope.app.fssync.testing import AppFSSyncLayer
from zope.app.fssync.testing import TestNetwork

checkoutdir = tempfile.mkdtemp(prefix='checkoutdir')
checkoutdir2 = tempfile.mkdtemp(prefix='checkoutdir2')

checker = renormalizing.RENormalizing([
    (re.compile(r"\\"), r"/"),
    ])

def setUp(test):
    module.setUp(test, 'zope.app.fssync.fssync_txt')
    if not os.path.exists(checkoutdir):
        os.mkdir(checkoutdir)
    if not os.path.exists(checkoutdir2):
        os.mkdir(checkoutdir2)

def tearDown(test):
    module.tearDown(test, 'zope.app.fssync.fssync_txt')
    shutil.rmtree(checkoutdir)
    shutil.rmtree(checkoutdir2)

def cleanUpTree(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)

def test_suite():

    globs = {'os': os,
            'zope':zope,
            'pprint': doctestunit.pprint,
            'checkoutdir':checkoutdir,
            'checkoutdir2': checkoutdir2,
            'cleanUpTree': cleanUpTree,
            'PublisherConnection': PublisherConnection,
            'TestNetwork': TestNetwork,
            'sleep': time.sleep}

    suite = unittest.TestSuite()

    for file in 'fssync.txt', 'security.txt', 'fssite.txt', 'merge.txt':
        test = functional.FunctionalDocFileSuite(file,
                    setUp=setUp, tearDown=tearDown,
                    globs=globs, checker=checker,
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS)
        test.layer = AppFSSyncLayer
        suite.addTest(test)

    if sys.platform != 'win32':
        test = functional.FunctionalDocFileSuite('fsmerge.txt',
                    setUp=setUp, tearDown=tearDown,
                    globs=globs, checker=checker,
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS)
        test.layer = AppFSSyncLayer
        suite.addTest(test)

    return suite

if __name__ == '__main__': unittest.main()
