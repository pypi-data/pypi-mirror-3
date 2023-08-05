# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cms.interfaces
import asm.cmsui.form
import grok
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
