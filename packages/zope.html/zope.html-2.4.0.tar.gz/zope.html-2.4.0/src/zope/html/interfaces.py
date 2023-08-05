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
"""Interfaces for zope.html.

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from i18n import _


class IEditableHtmlInformation(zope.interface.Interface):
    """Information about an HTML file or fragment."""

    isFragment = zope.schema.Bool(
        title=_("Is fragment?"),
        description=_("Set to true if the HTML should be handled as a"
                      " fragment to be composed to create a document."),
        required=True,
        readonly=False,
        )
