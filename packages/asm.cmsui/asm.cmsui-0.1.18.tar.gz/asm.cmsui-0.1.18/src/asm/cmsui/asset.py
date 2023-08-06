# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.blob
import asm.cms.asset
import asm.cms.utils
import asm.cmsui.base
import asm.cmsui.form
import asm.cmsui.interfaces
import cgi
import grok
import magic
import os
import urllib
import zope.app.form.browser.textwidgets

grok.context(asm.cms.asset.Asset)


class FileWithDisplayWidget(zope.app.form.browser.textwidgets.FileWidget):

    def __call__(self):
        html = super(FileWithDisplayWidget, self).__call__()
        # XXX news stories have teaser images where this breaks. This is a hack
        # to get around that ASAP.
        return html
        field = self.context
        asset = field.context

        if asset.content_type is None:
            return html
        if not asset.content_type.startswith("image/"):
            return html

        image_datauri = asm.cms.interfaces.IDataUri(asset).datauri
        img = ''
        if image_datauri:
            img = ('<br/><img src="%s"/>' % image_datauri)
        return (html + img)

    def _toFieldValue(self, input):
        if input == self._missing:
            # Use existing value, don't override with missing.
            field = self.context
            asset = field.context
            value = field.get(asset)
        else:
            value = ZODB.blob.Blob()
            f = value.open('w')
            f.write(input.read())
            f.close()
        return value

class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.name('edit')

    main_fields = grok.AutoFields(asm.cms.asset.Asset).select(
        'title', 'content')


class Index(grok.View):

    grok.layer(grok.IDefaultBrowserLayer)
    grok.name('index')

    def update(self):
        self.response.setHeader('Content-Type', self.context.content_type)

        modified = asm.cms.utils.datetime_to_http_timestamp(self.context.modified)
        self.response.setHeader('Last-Modified', modified)

        filedata = open(self.context.content.committed())
        filedata.seek(0, os.SEEK_END)
        self.response.setHeader('Content-Length', filedata.tell())
        filedata.seek(0)
        self.filedata = filedata

    def render(self):
        return self.filedata


class ImagePicker(grok.View):
    grok.name('image-picker')


class DownloadAction(grok.Viewlet):
    grok.viewletmanager(asm.cmsui.base.ExtendedPageActions)

    @property
    def applicable(self):
        try:
            self.context.content.committed()
        except AttributeError:
            return False
        return True


class Download(Index):
    """Adds headers that enable downloading of assets.

    This just wraps the index view and executes its update and render functions
    as the index view would execute them normally.
    """

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.name('download')

    def update(self, *args, **kw):
        self.response.setHeader("Content-Type", "application/force-download")
        self.response.setHeader("Content-Type", "application/octet-stream")
        self.response.setHeader("Content-Transfer-Encoding", "binary")
        self.response.setHeader("Content-Description", "File Transfer")
        filename = urllib.quote_plus(self.context.page.__name__)
        self.response.setHeader("Content-Disposition", "attachment; filename=%s" % filename)
        return super(Download, self).update(*args, **kw)

    def render(self, *args, **kw):
        return super(Download, self).render(*args, **kw)


def searchable_text(asset):
    if asset.tags is not None and "hide-search" in asset.tags:
        return ""

    result = asset.title + " "

    if asset.tags is not None:
        tags = asset.tags.split(' ')
        result += " ".join("tag:" + tag for tag in tags)

    return result

class TextIndexing(grok.Adapter):

    zope.interface.implements(asm.cms.interfaces.ISearchableText)

    def __init__(self, asset):
        self.body = searchable_text(asset)

class SearchPreview(grok.View):

    def update(self, q):
        self.keyword = q

    def render(self):
        # TODO this is a quite crude hack to enable search result display.
        # It doesn't take into account different order of words or multiple
        # words that are used in the query.

        text = searchable_text(self.context)

        focus = text.lower().find(self.keyword.lower())

        if focus == -1:
            return cgi.escape(text)

        result = '<span class="match">%s</span>' % \
            cgi.escape(text[focus:(focus + len(self.keyword))])

        return result
