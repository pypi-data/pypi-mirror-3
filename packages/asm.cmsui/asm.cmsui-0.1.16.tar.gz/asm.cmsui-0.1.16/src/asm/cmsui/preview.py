# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import zope.interface
import asm.cmsui.interfaces
import zope.component
import zope.intid


class IntId(grok.View):

    grok.context(zope.interface.Interface)   # XXX Meh.
    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def render(self):
        intids = zope.component.getUtility(zope.intid.IIntIds)
        return intids.getId(self.context)
