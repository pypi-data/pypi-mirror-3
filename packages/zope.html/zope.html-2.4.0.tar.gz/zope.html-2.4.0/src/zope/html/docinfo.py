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
"""Helper functions to get information on the current document.

"""
__docformat__ = "reStructuredText"

import HTMLParser
import xml.parsers.expat

import persistent.dict

import zope.annotation.interfaces
import zope.file.interfaces
import zope.html.interfaces
import zope.interface
import zope.mimetype.types


# Use the package name as the annotation key:
KEY = __name__.rsplit(".", 1)[0]


class EditableHtmlInformation(object):

    zope.interface.implements(
        zope.html.interfaces.IEditableHtmlInformation)

    _annotations = None

    def __init__(self, file):
        self.__parent__ = file
        self.context = file

    def _get_annotation(self):
        if self._annotations is None:
            self._annotations = zope.annotation.interfaces.IAnnotations(
                self.context)
        return self._annotations.get(KEY)

    def _get_isFragment(self):
        annotation = self._get_annotation()
        if annotation is not None:
            if "is_fragment" in annotation:
                return annotation["is_fragment"]
        # compute from data
        f = zope.file.interfaces.IFile(self.context)
        if zope.mimetype.types.IContentTypeTextHtml.providedBy(self.context):
            isfrag = _is_html_fragment(f)
        else:
            isfrag = _is_xhtml_fragment(f)
        return isfrag

    def _set_isFragment(self, value):
        value = bool(value)
        if value != self.isFragment:
            annotation = self._get_annotation()
            if annotation is None:
                annotation = persistent.dict.PersistentDict()
            annotation["is_fragment"] = value
            self._annotations[KEY] = annotation

    isFragment = property(_get_isFragment, _set_isFragment)


def _is_xhtml_fragment(file):
    f = file.open("r")
    p = xml.parsers.expat.ParserCreate()
    h = HTMLContentSniffer()
    p.StartElementHandler = h.handle_starttag
    p.CharacterDataHandler = h.handle_data
    try:
        p.Parse(f.read(2048))
    except xml.parsers.expat.ExpatError:
        # well-formedness failure; don't even pretend it might be a
        # document (might not be a useful fragment either, though)
        return True
    return p.leading_content or p.first_element != "html"


def _is_html_fragment(file):
    """Return True iff `file` represents an HTML fragment."""
    f = file.open("r")
    p = HTMLContentSniffer()
    p.feed(f.read(2048))
    return p.leading_content or p.first_element != "html"


class HTMLContentSniffer(HTMLParser.HTMLParser):

    first_element = None
    leading_content = None

    def handle_starttag(self, name, attrs):
        if not self.first_element:
            self.first_element = name

    def handle_data(self, data):
        if not self.first_element:
            data = data.strip()
            if data:
                self.leading_content = True
