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
"""Browser views that implement editing and preview.

"""
__docformat__ = "reStructuredText"

import datetime

import zope.lifecycleevent
import zope.event
import zope.file.contenttype
import zope.file.interfaces
import zope.formlib.form
import zope.html.field
import zope.html.interfaces
import zope.mimetype.interfaces

from zope import mimetype
from zope.interface.common import idatetime

from i18n import _


UNIVERSAL_CHARSETS = ("utf-8", "utf-16", "utf-16be", "utf-16le")


def get_rendered_text(form):
    f = form.context.open("r")
    data = f.read()
    f.close()
    ci = mimetype.interfaces.IContentInfo(form.context)
    return ci.decode(data)


class BaseEditingView(zope.formlib.form.Form):

    # initial value helpers:

    def get_rendered_isFragment(self):
        info = zope.html.interfaces.IEditableHtmlInformation(self.context)
        return info.isFragment

    def get_rendered_encoding(self):
        charset = self.context.parameters.get("charset")
        if charset:
            return zope.component.queryUtility(
                mimetype.interfaces.ICharsetCodec, charset)
        else:
            return None

    # field definitions:

    view_fields = zope.formlib.form.Fields(
        zope.html.interfaces.IEditableHtmlInformation,
        )
    view_fields["isFragment"].get_rendered = get_rendered_isFragment

    encoding_field = zope.formlib.form.Field(
        zope.schema.Choice(
            __name__=_("encoding"),
            title=_("Encoding"),
            description=_("Character data encoding"),
            source=mimetype.source.codecSource,
            required=False,
            ))
    encoding_field.get_rendered = get_rendered_encoding

    reencode_field = zope.formlib.form.Field(
        zope.schema.Bool(
            __name__="reencode",
            title=_("Re-encode"),
            description=_("Enable encoding the text using UTF-8"
                          " instead of the original encoding."),
            default=False,
            )
        )

    msgCannotDecodeText = _("Can't decode text for editing; please specify"
                            " the document encoding.")

    def setUpWidgets(self, ignore_request=False):
        ci = mimetype.interfaces.IContentInfo(self.context)
        self.have_text = "charset" in ci.effectiveParameters
        fields = [self.view_fields]
        if self.have_text:
            if self.get_rendered_isFragment():
                text_field = self.fragment_field
            else:
                text_field = self.document_field
            fields.append(text_field)
            if ci.effectiveParameters.get("charset") not in UNIVERSAL_CHARSETS:
                fields.append(self.reencode_field)
        else:
            if not self.status:
                self.status = self.msgCannotDecodeText
            fields.append(self.encoding_field)
        self.form_fields = zope.formlib.form.Fields(*fields)
        super(BaseEditingView, self).setUpWidgets(
            ignore_request=ignore_request)

    def save_validator(self, action, data):
        errs = self.validate(None, data)
        if not self.have_text:
            ifaces = zope.interface.providedBy(
                zope.security.proxy.removeSecurityProxy(self.context))
            for iface in ifaces:
                if mimetype.interfaces.IContentTypeInterface.providedBy(iface):
                    break
            else:
                # Should never happen!
                assert False, "this view has been mis-registered!"
            errs += zope.file.contenttype.validateCodecUse(
                self.context, iface, data.get("encoding"),
                self.encoding_field)
        return errs

    @zope.formlib.form.action(_("Save"), validator=save_validator)
    def save(self, action, data):
        changed = False
        context = self.context

        if self.have_text:
            changed = self.handle_text_update(data)
        else:
            # maybe we have a new encoding?
            codec = data["encoding"]
            if codec is None:
                self.status = self.msgCannotDecodeText
            else:
                if "charset" in context.parameters:
                    old_codec = zope.component.queryUtility(
                        mimetype.interfaces.ICharsetCodec,
                        context.parameters["charset"])
                else:
                    old_codec = None
                if getattr(old_codec, "name", None) != codec.name:
                    # use the preferred charset for the new codec
                    new_charset = zope.component.getUtility(
                        mimetype.interfaces.ICodecPreferredCharset,
                        codec.name)
                    parameters = dict(context.parameters)
                    parameters["charset"] = new_charset.name
                    context.parameters = parameters
                    changed = True

        # Deal with the isFragment flag:
        info = zope.html.interfaces.IEditableHtmlInformation(context)
        isFragment = data["isFragment"]
        if isFragment != info.isFragment:
            info.isFragment = data["isFragment"]
            changed = True

        # Set the status message:
        if changed:
            # Should this get done if only the isFragment changed?
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(context))
            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')
            now = datetime.datetime.now(idatetime.ITZInfo(self.request))
            self.status = _("Updated on ${date_time}",
                            mapping={'date_time': formatter.format(now)})
        elif not self.status:
            self.status = _('No changes')

    def handle_text_update(self, data):
        text = data["text"]
        if text != get_rendered_text(self):
            ci = mimetype.interfaces.IContentInfo(self.context)
            codec = ci.getCodec()
            try:
                textdata, consumed = codec.encode(text)
                if consumed != len(text):
                    # XXX borked!
                    pass
            except:
                # The old encoding will no longer support the data, so
                # switch to UTF-8:
                if data.get("reencode"):
                    textdata = text.encode("utf-8")
                    parameters = dict(self.context.parameters)
                    parameters["charset"] = "utf-8"
                    self.context.parameters = parameters
                else:
                    encoding = ci.effectiveParameters["charset"]
                    self.status = _(
                        "Can't encode text in current encoding (${encoding})"
                        "; check 'Re-encode' to enable conversion to UTF-8.",
                        mapping={"encoding": encoding})
                    self.form_reset = False
                    return False
            # need to discard re-encode checkbox
            f = self.context.open("w")
            f.write(textdata)
            f.close()
            return True


class HtmlEditingView(BaseEditingView):
    """Editing view for HTML content."""

    document_field = zope.formlib.form.Field(
        zope.html.field.HtmlDocument(
            __name__="text",
            title=_("Text"),
            description=_("Text of the document being edited."),
            )
        )
    document_field.get_rendered = get_rendered_text

    fragment_field = zope.formlib.form.Field(
        zope.html.field.HtmlFragment(
            __name__="text",
            title=_("Text"),
            description=_("Text of the fragment being edited."),
            )
        )
    fragment_field.get_rendered = get_rendered_text


class XhtmlEditingView(BaseEditingView):
    """Editing view for XHTML content."""

    document_field = zope.formlib.form.Field(
        zope.html.field.XhtmlDocument(
            __name__="text",
            title=_("Text"),
            description=_("Text of the document being edited."),
            )
        )
    document_field.get_rendered = get_rendered_text

    fragment_field = zope.formlib.form.Field(
        zope.html.field.XhtmlFragment(
            __name__="text",
            title=_("Text"),
            description=_("Text of the fragment being edited."),
            )
        )
    fragment_field.get_rendered = get_rendered_text
