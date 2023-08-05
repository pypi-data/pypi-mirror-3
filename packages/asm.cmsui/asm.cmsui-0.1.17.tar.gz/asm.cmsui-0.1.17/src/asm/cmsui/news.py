# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cmsui.form
import asm.cmsui.retail
import asm.cms.news
import grok

grok.context(asm.cms.news.NewsFolder)


class Edit(asm.cmsui.form.EditForm):

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title', 'tags')


class Index(asm.cmsui.retail.Pagelet):

    def list(self):
        for news in reversed(list(self.context.list())):
            edition = asm.cms.edition.select_edition(news, self.request)
            if isinstance(edition, asm.cms.edition.NullEdition):
                continue
            yield edition
