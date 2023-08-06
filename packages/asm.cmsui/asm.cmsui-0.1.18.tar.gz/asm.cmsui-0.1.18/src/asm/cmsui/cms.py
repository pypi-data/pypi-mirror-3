# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cms.interfaces
import asm.cmsui.form
import grok
import simplejson
import zope.catalog.interfaces
import zope.component
import zope.interface


grok.context(asm.cms.cms.CMS)


class SelectProfile(asm.cmsui.form.EditForm):

    form_fields = grok.AutoFields(asm.cms.interfaces.IProfileSelection)


class PreviewWindow(grok.View):

    grok.name('preview-window')
    grok.template('preview-window')


class ToolActions(grok.Viewlet):

    grok.template('actions')
    grok.viewletmanager(asm.cmsui.base.NavigationToolActions)
    grok.context(zope.interface.Interface)


class TagsJson(grok.View):
    grok.context(asm.cms.interfaces.ICMS)
    grok.name('tags.json')

    def render(self):
        catalog = zope.component.getUtility(
            zope.catalog.interfaces.ICatalog, name='edition_catalog')
        return simplejson.dumps(list(catalog['tags'].values()))
