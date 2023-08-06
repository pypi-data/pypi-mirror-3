# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import asm.cmsui.base
import asm.cmsui.interfaces
import grok
import zope.interface
import megrok.pagelet


class ExtendedPageActions(grok.Viewlet):

    grok.viewletmanager(asm.cmsui.base.ExtendedPageActions)
    grok.context(asm.cms.edition.Edition)


# Issue #59: The following viewlet setup is a bit annoying: we register a
# viewlet for displaying all editions when looking at a page and when looking
# at a specific edition. The code is basically the same each time (we actually
# re-use the template), but the amount of registration necessary is just bad.


class Editions(grok.ViewletManager):

    grok.name('editions')
    grok.context(zope.interface.Interface)


class PageEditions(grok.Viewlet):
    grok.viewletmanager(Editions)
    grok.context(zope.interface.Interface)
    grok.template('editions')


class NullEdit(megrok.pagelet.Pagelet):
    """This pagelet will be displayed as the edit view for all editions
    for which no specific edit view exists.

    It is mainly intended to support developers to incrementally develop
    products without having to deal with broken UIs in the intermediate
    stages.

    """

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.name('edit')
    grok.context(zope.interface.Interface)

    def render(self):
        return ''


class NullIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.name('index')
    grok.context(asm.cms.edition.NullEdition)

    def render(self):
        return 'No edition available.'


class EditionIndex(megrok.pagelet.Pagelet):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.name('index')
    grok.context(asm.cms.interfaces.IEdition)

    def render(self):
        self.redirect(self.url(self.context, '@@edit'))


class DisplayParameters(grok.View):
    grok.context(asm.cms.edition.EditionParameters)
    grok.name('index')

    def render(self):
        # XXX use better lookup mechanism for tag labels
        tags = sorted(self.context)
        labels = zope.component.getUtility(asm.cms.interfaces.IEditionLabels)
        return '(%s)' % ', '.join(labels.lookup(tag) for tag in tags)


class Delete(grok.View):
    """Deletes an edition."""

    grok.context(asm.cms.edition.Edition)

    def update(self):
        page = self.context.__parent__
        self.target = asm.cms.edition.select_edition(
            page, self.request)
        del page[self.context.__name__]

    def render(self):
        self.redirect(self.url(self.target, '@@edit'))


class ImagePicker(grok.View):
    grok.context(asm.cms.edition.Edition)
    grok.name('image-picker')



