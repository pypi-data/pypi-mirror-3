##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import os
import re
import unittest
import zc.zk.testing
import zope.testing.setupstack
import zope.testing.renormalizing

def setUp(test):
    zope.testing.setupstack.setUpDirectory(test)
    os.mkdir('testdirectory')
    os.chdir('testdirectory')
    os.mkdir('parts')
    zc.zk.testing.setUp(test, tree='/zookeeper\n  buildout:path="/xxxxxxxxx"')
    test.globs['ZooKeeper'].connection_strings.add('127.0.0.1:2181')
    test.globs['ZooKeeper'].connection_strings.add('localhost:2181')


def tearDown(test):
    zc.zk.testing.tearDown(test)
    zope.testing.setupstack.tearDown(test)

def test_suite():
    checker = zope.testing.renormalizing.RENormalizing([
        (re.compile(r'(/\w+)+/testdirectory/'), '/testdirectory/'),
        # (re.compile(r''), ''),
        # (re.compile(r''), ''),
        ])
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel(checker=checker) + manuel.capture.Manuel(),
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            ),
        ))

