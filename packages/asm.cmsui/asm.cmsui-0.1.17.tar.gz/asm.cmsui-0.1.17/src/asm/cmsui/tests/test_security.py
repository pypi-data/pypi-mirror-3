# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.testing
import asm.cmsui.interfaces
import unittest
import z3c.template.template
import zope.interface
import zope.security.checker


class SecurityTests(unittest.TestCase):

    layer = asm.cms.testing.TestLayer

    exceptions = [z3c.template.template.TemplateFactory]

    def test_cms_skin_protected(self):
        # All views in the CMS skin are supposed to be protected by
        # 'asm.cms.EditContent' permission.
        for registration in zope.component.globalSiteManager.registeredAdapters():
            if len(registration.required) != 2:
                continue
            if registration.required[1] is not asm.cmsui.interfaces.ICMSSkin:
                continue
            if registration.factory.__class__ in self.exceptions:
                continue
            view = registration.factory(object(), object())
            checker = zope.security.checker.selectChecker(view)
            self.assertEquals(
                'asm.cms.EditContent', checker.get_permissions.get('__call__'),
                'Missing protection for %r' % registration.factory)
