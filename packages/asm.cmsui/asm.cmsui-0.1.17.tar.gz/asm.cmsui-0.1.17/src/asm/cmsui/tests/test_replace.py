# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cms.htmlpage
import asm.cms.replace
import asm.cmsui.testing
import transaction
import unittest


class ReplaceSelenium(asm.cmsui.testing.SeleniumTestCase):

    def test_simple_replace(self):
        home = self.cms.editions.next()
        home.title = 'testing homepage'
        home.content = 'foobar'
        transaction.commit()
        s = self.selenium
        s.open('http://mgr:mgrpw@%s/++skin++cms/cms' % s.server)
        s.click('css=.toggle-navigation')
        s.verifyNotVisible('css=#search-and-replace')
        s.click('css=#tools h3')
        s.clickAndWait('css=#search-and-replace')
        self.assertEquals(
            'http://%s/++skin++cms/cms/@@searchandreplace' % s.server,
            s.getLocation())
        s.type('name=search', 'foo')
        s.type('name=replace', 'bar')
        s.clickAndWait('name=form.actions.search')
        s.assertTextPresent('testing homepage')
        s.assertElementPresent('name=occurrences')
        s.clickAndWait('name=form.actions.replace')

        s.assertTextPresent('Replaced 1 occurrences.')
        self.assertEquals(
            'http://%s/++skin++cms/cms/searchandreplace' % s.server,
            s.getLocation())

        transaction.begin()
        self.assertEquals('barbar', home.content)
