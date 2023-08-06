#prox Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.edition
import asm.cms.interfaces
import asm.cmsui.base
import asm.cmsui.interfaces
import grok
import megrok.pagelet
import z3c.flashmessage.interfaces
import zope.interface
import zope.security


class PublicLayoutHelper(grok.View):
    grok.context(zope.interface.Interface)
    grok.layer(asm.cmsui.interfaces.IRetailSkin)

    def render(self):
        return ''
