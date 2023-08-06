# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cmsui.form
import asm.cmsui.interfaces
import asm.cms.homepage
import grok


class Edit(asm.cmsui.form.EditionEditForm):

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')
    grok.context(asm.cms.homepage.Homepage)

    form_fields = grok.AutoFields(asm.cms.interfaces.IEdition).select(
        'title')
