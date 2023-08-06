# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cms.importer
import asm.cmsui.base
import asm.cmsui.form
import grok
import transaction
import zope.interface

class ImportActions(grok.Viewlet):

    grok.viewletmanager(asm.cmsui.base.NavigationToolActions)
    grok.context(zope.interface.Interface)


class Import(asm.cmsui.form.Form):

    grok.context(asm.cms.cms.CMS)
    form_fields = grok.AutoFields(asm.cms.interfaces.IImport)

    display_max_errors = 5

    @grok.action(u'Import')
    def import_action(self, data):
        importer = asm.cms.importer.Importer(self.context, data)

        errors = importer()
        if len(errors) > 0:
            transaction.abort()

        if len(errors) > 0:
            self.flash(u"Aborted import due to following errors:")
        if len(errors) > self.display_max_errors:
            self.flash(u"Too many errors detected. Displaying the first %d errors." % self.display_max_errors)
        for error in errors[:self.display_max_errors]:
            self.flash(error, "warning")

        if len(errors) == 0:
            self.flash('Imported content successfully.')
