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
from zope.testing import setupstack
import doctest
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import os
import unittest
import zc.s3uploadqueue

def write(path, s):
    with open(path, 'w') as f:
        f.write(s)

def setup(test):
    setupstack.setUpDirectory(test)
    s3conn = setupstack.context_manager(
        test, mock.patch('boto.s3.connection.S3Connection'))
    s3conn = setupstack.context_manager(
        test, mock.patch('boto.s3.key.Key'))


def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'README.txt',
            globs={'write': write},
            setUp=setup, tearDown=setupstack.tearDown,
            ),
        ))





