# Copyright (c) 2011 Assembly Organizing
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.redirect
import asm.cmsui.interfaces
import grok
import zope.component
import zope.publisher.interfaces.browser
import zope.traversing.browser.interfaces

grok.context(asm.cms.redirect.Redirect)

class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.name('edit')

    main_fields = grok.AutoFields(asm.cms.redirect.Redirect).select(
        'title', 'target_url')

class Index(grok.View):

    grok.layer(grok.IDefaultBrowserLayer)
    grok.name('index')

    def update(self):
        self.redirect(self.context.target_url, trusted=True)

    def render(self):
        return '<a href="%s">%s</a>' % (self.context.target_url, self.context.target_url)

class RedirectAbsoluteUrl(grok.MultiAdapter):
    grok.adapts(
        asm.cms.interfaces.IRedirect,
        asm.cmsui.interfaces.IRetailBaseSkin)
    grok.implements(zope.traversing.browser.interfaces.IAbsoluteURL)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.context.target_url
