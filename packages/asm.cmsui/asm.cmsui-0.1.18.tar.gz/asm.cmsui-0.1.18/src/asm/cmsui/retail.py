# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cmsui.interfaces
import grok
import megrok.pagelet
import zope.app.publication.interfaces
import zope.interface
import zope.app.folder.interfaces


class Layout(megrok.pagelet.Layout):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cmsui.interfaces.IRetailSkin)

    megrok.pagelet.template('templates/retail.pt')


class Pagelet(megrok.pagelet.Pagelet):

    grok.baseclass()
    grok.layer(asm.cmsui.interfaces.IRetailSkin)


class RetailTraverser(grok.Traverser):
    """Retail traversers try to map URLs to page *editions* when the URL would
    normally point to a page.

    We also hide the editions' real URLs and point them to the pages' URLs.

    """

    grok.baseclass()

    # This directive is currently ignored due to LP #408819. See workaround
    # below.
    grok.layer(asm.cmsui.interfaces.IRetailBaseSkin)

    def traverse(self, name):
        if not asm.cmsui.interfaces.IRetailBaseSkin.providedBy(self.request):
            # Workaround for grok.layer bug
            return
        page = self.get_context()
        subpage = page.get(name)
        if not asm.cms.interfaces.IPage.providedBy(subpage):
            return
        return asm.cms.edition.select_edition(subpage, self.request)

    def get_context(self):
        return self.context


class RootTraverse(RetailTraverser):

    grok.context(zope.app.folder.interfaces.IRootFolder)
    # Another workaround to #408819 as someone else already registers a view
    # on the default skin.
    grok.baseclass()


class PageTraverse(RetailTraverser):

    grok.context(asm.cms.interfaces.IPage)


class EditionTraverse(RetailTraverser):

    grok.context(asm.cms.interfaces.IEdition)

    def get_context(self):
        return self.context.page


@grok.adapter(asm.cms.interfaces.IEdition, asm.cmsui.interfaces.IRetailBaseSkin)
@grok.implementer(zope.traversing.browser.interfaces.IAbsoluteURL)
def edition_url(edition, request):
    return zope.component.getMultiAdapter(
        (edition.__parent__, request),
        zope.traversing.browser.interfaces.IAbsoluteURL)


@grok.subscribe(zope.publisher.interfaces.http.IHTTPVirtualHostChangedEvent)
def fix_virtual_host(event):
    if not asm.cmsui.interfaces.IRetailBaseSkin.providedBy(event.request):
        return
    root = event.request.getVirtualHostRoot()
    if asm.cms.interfaces.IEdition.providedBy(root):
        # XXX This is extremely hacky but the APIs don't allow me to do
        # better.
        event.request._vh_root = root.__parent__


@grok.subscribe(zope.app.publication.interfaces.IBeforeTraverseEvent)
def propagate_before_traverse_to_pages(event):
    if not asm.cms.interfaces.IEdition.providedBy(event.object):
        return
    notification = zope.app.publication.interfaces.BeforeTraverseEvent(
        event.object.__parent__, event.request)
    zope.event.notify(notification)
