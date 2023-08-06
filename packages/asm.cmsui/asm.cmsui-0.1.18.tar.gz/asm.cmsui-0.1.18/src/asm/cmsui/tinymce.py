# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.form.browser.textwidgets
import asm.cms.interfaces
import grok


class TinyMCEWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    mce_class = 'mceEditor'

    def __call__(self):
        self.cssClass += ' %s' % self.mce_class
        return super(TinyMCEWidget, self).__call__()

class TinyMCEWidgetSmall(TinyMCEWidget):

    mce_class = 'mceEditorSmall'


class TinyMCELinkBrowser(grok.View):

    grok.context(asm.cms.interfaces.IPage)
    grok.name('tinymce-linkbrowser')
    grok.template('linkbrowser')

    def pages(self):
        # Return a set of editions representing the pages
        for page in self.context.subpages:
            yield asm.cms.edition.select_edition(page, self.request)

    def breadcrumbs(self):
        result = []
        current = self.context
        while True:
            result.insert(0,
                asm.cms.edition.select_edition(current, self.request))
            if current is self.application:
                break
            current = current.__parent__
        return result
