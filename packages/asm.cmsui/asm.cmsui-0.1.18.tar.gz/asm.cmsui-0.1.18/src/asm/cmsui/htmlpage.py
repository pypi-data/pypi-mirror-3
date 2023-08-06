# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.htmlpage
import asm.cmsui.interfaces
import asm.cmsui.retail
import asm.cmsui.form
import asm.cmsui.tinymce
import cgi
import grok
import lxml.etree

grok.context(asm.cms.htmlpage.HTMLPage)


class Index(asm.cmsui.retail.Pagelet):
    grok.layer(asm.cmsui.interfaces.IRetailSkin)


class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    main_fields = grok.AutoFields(asm.cms.htmlpage.HTMLPage).select(
        'title', 'description', 'content')
    main_fields['description'].custom_widget = (
        asm.cmsui.tinymce.TinyMCEWidgetSmall)
    main_fields['content'].custom_widget = asm.cmsui.tinymce.TinyMCEWidget

    def post_process(self):
        self.content = asm.cms.htmlpage.fix_relative_links(
            self.context.content, self.url(self.context))


class SearchPreview(grok.View):

    PREVIEW_AMOUNT = 50

    def update(self, q):
        self.keyword = q

    def render(self):
        try:
            tree = lxml.etree.fromstring(
                '<stupidcafebabe>%s</stupidcafebabe>' % self.context.content)
        except Exception:
            return ''
        text = ''.join(tree.itertext())

        # Select limited amount of characters
        focus = text.lower().find(self.keyword.lower())
        if focus == -1:
            return cgi.escape(text[:2*self.PREVIEW_AMOUNT])
        text = text[
            max(focus - self.PREVIEW_AMOUNT, 0):(focus + self.PREVIEW_AMOUNT)]

        # Insert highlighting. Recompute offset of focus with shorter text.
        focus = text.lower().find(self.keyword.lower())
        pre, keyword, post = (text[:focus],
                              text[focus:focus + len(self.keyword)],
                              text[focus + len(self.keyword):])
        text = '%s<span class="match">%s</span>%s' % \
            tuple(map(cgi.escape, [pre, keyword, post]))
        return text

class ExtendedPageActions(grok.Viewlet):

    grok.viewletmanager(asm.cmsui.base.ExtendedPageActions)
