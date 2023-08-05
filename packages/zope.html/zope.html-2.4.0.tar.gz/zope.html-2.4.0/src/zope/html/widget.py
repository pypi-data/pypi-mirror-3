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
"""Widget implementations for rich-text fields.

"""
__docformat__ = "reStructuredText"

import zope.app.form.browser

import zc.resourcelibrary


class FckeditorWidget(zope.formlib.widgets.TextAreaWidget):

    editorWidth = 600
    editorHeight = 400
    fckVersion = '2.6.4.1'

    configurationPath = "/@@/zope_fckconfig.js"
    toolbarConfiguration = "zope"

    def __call__(self):
        zc.resourcelibrary.need("fckeditor")
        #
        # XXX The 'shortname' here needs some salt to ensure that
        # multiple widgets with the same trailing name are
        # distinguishable; some encoding of the full name seems
        # appropriate, or a per-request counter would also do nicely.
        #
        d = {
            "config": self.configurationPath,
            "name": self.name,
            "shortname": self.name.split('.', 1)[-1],
            "toolbars": self.toolbarConfiguration,
            "width": self.editorWidth,
            "height": self.editorHeight,
            "fckversion": self.fckVersion,
            }
        textarea = super(FckeditorWidget, self).__call__()
        return textarea + (self.javascriptTemplate % d)

    javascriptTemplate = '''
<script type="text/javascript" language="JavaScript">
var oFCKeditor_%(shortname)s = new FCKeditor(
        "%(name)s", %(width)s, %(height)s, "%(toolbars)s");
    oFCKeditor_%(shortname)s.BasePath = "/@@/fckeditor/%(fckversion)s/fckeditor/";
    oFCKeditor_%(shortname)s.Config["CustomConfigurationsPath"] = "%(config)s";
    oFCKeditor_%(shortname)s.ReplaceTextarea();
</script>
'''

class CkeditorWidget(zope.formlib.widgets.TextAreaWidget):

    editorHeight = 400
    fckVersion = '3.6.2'

    configurationPath = "/@@/zope_ckconfig.js"

    def __call__(self):
        zc.resourcelibrary.need("ckeditor")
        #
        # XXX The 'shortname' here needs some salt to ensure that
        # multiple widgets with the same trailing name are
        # distinguishable; some encoding of the full name seems
        # appropriate, or a per-request counter would also do nicely.
        #
        d = {
            "config": self.configurationPath,
            "name": self.name,
            "shortname": self.name.split('.', 1)[-1],
            "height": self.editorHeight,
            "fckversion": self.fckVersion,
            }
        textarea = super(CkeditorWidget, self).__call__()
        return textarea + (self.javascriptTemplate % d)

    javascriptTemplate = '''
<script type="text/javascript" language="JavaScript">
var CKeditor_%(shortname)s = new CKEDITOR.replace("%(name)s",
    {
        height: %(height)s,
        customConfig : "%(config)s",
    }
);
</script>
'''
