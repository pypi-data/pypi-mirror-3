##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Test harness for zope.html.

"""
__docformat__ = "reStructuredText"

import os
import unittest
import doctest

import pytz

import zope.annotation.attribute
import zope.formlib.tests.test_textareawidget
import zope.app.testing.placelesssetup
import zope.component
import zope.file.testing
import zope.interface.common.idatetime
import zope.mimetype.types
import zope.publisher.interfaces

from zope.app.testing import functional

import zope.html.widget


class FckeditorWidgetTestCase(
    zope.formlib.tests.test_textareawidget.TextAreaWidgetTest):

    _WidgetFactory = zope.html.widget.FckeditorWidget


def setUp(test):
    zope.app.testing.placelesssetup.setUp()
    zope.component.provideAdapter(
        zope.annotation.attribute.AttributeAnnotations)
    # we have to initialize the mimetype handling
    zope.mimetype.types.setup()


def tearDown(test):
    zope.app.testing.placelesssetup.tearDown()


@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
def requestToTZInfo(request):
    return pytz.timezone('US/Eastern')

EditableHtmlLayer = zope.file.testing.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, "EditableHtmlLayer")


def test_suite():
    ftests = zope.file.testing.FunctionalBlobDocFileSuite("browser.txt")
    ftests.layer = EditableHtmlLayer
    return unittest.TestSuite([
        doctest.DocFileSuite(
            "docinfo.txt",
            setUp=setUp,
            tearDown=tearDown),
        doctest.DocFileSuite(
            "widget.txt",
            optionflags=(doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)),
        unittest.makeSuite(FckeditorWidgetTestCase),
        ftests,
        ])
