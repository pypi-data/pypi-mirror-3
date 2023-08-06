##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Tests for zope.app.fssync.folder.adapter.

$Id: tests.py 76675 2007-06-14 07:05:37Z oestermeier $
"""

import unittest
from zope.testing import doctest
from zope.testing import doctestunit


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS
    return doctestunit.DocTestSuite('zope.app.fssync.folder.adapter',
                                        optionflags=flags)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
