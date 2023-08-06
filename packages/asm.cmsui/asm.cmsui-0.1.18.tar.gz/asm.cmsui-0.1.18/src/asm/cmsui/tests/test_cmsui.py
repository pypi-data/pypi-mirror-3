# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.page
import asm.cmsui.testing
import grok
import transaction
import unittest
import zope.event


class CMSUI(asm.cmsui.testing.SeleniumTestCase):

    def test_cms_redirects_to_editor(self):
        self.selenium.open('http://mgr:mgrpw@%s/++skin++cms/cms' %
                           self.selenium.server)
        self.assertEquals(
            u'http://%s/++skin++cms/cms/edition-/@@edit' %
                self.selenium.server,
            self.selenium.getLocation())

    def test_switch_to_navigation_and_back(self):
        s = self.selenium
        s.assertNotVisible("css=#navigation")
        s.assertVisible("css=#content")

        s.click('css=.toggle-navigation')
        s.assertVisible("css=#navigation")
        s.assertNotVisible("css=#content")

        s.click('css=.toggle-navigation')
        s.assertNotVisible("css=#navigation")
        s.assertVisible("css=#content")

    def test_breadcrumbs(self):
        # We need to add a sub-page as the root never shows up in the
        # breadcrumbs
        self.cms['xy'] = asm.cms.page.Page('htmlpage')
        self.cms['xy'].editions.next().title = u'A test page'
        transaction.commit()
        s = self.selenium
        s.open(
            'http://mgr:mgrpw@%s/++skin++cms/cms/xy/edition-/@@edit' %
            s.server)
        s.assertVisible(
            'xpath=//div[contains(@class, "breadcrumbs")]/'
            'a[contains(text(), "A test page")]')
        s.clickAndWait(
            'xpath=//div[contains(@class, "breadcrumbs")]/'
            'a[contains(text(), "A test page")]')
        s.assertElementPresent('name=form.actions.save')

    def test_additional_form_fields(self):
        s = self.selenium
        s.assertVisible('//h3[contains(text(), "Tags")]')
        s.assertNotVisible('name=form.tags')
        s.click('//h3[contains(text(), "Tags")]')
        s.assertVisible('name=form.tags')

    def test_search_no_results(self):
        s = self.selenium
        s.type('name=q', 'asdf')
        s.selenium.key_press('name=q', r'\13')
        s.waitForPageToLoad()
        s.waitForTextPresent(
            'The search for "asdf" returned')
        s.assertTextPresent('no results.')

    def test_search_result_preview_htmlpage(self):
        edition = self.cms.editions.next()
        edition.content = 'sometext asdf someothertext'
        edition.title = u'Something going on'
        zope.event.notify(grok.ObjectModifiedEvent(edition))
        transaction.commit()
        s = self.selenium
        s.type('name=q', 'asdf')
        s.selenium.key_press('name=q', r'\13')
        s.waitForPageToLoad()
        s.assertTextPresent('Something going on')

    def test_change_page_type(self):
        s = self.selenium
        s.assertNotVisible('xpath=//input[@value="Change page type"]')
        s.click('//h3[contains(text(), "Page")]/following-sibling::div[@class="opener"]')
        s.assertVisible('xpath=//input[@value="Change page type"]')
        s.clickAndWait('xpath=//input[@value="Change page type"]')
        s.click('id=form.type.0') # Redirect section
        s.clickAndWait('name=form.actions.change')
        self.assertEquals(
            'http://%s/++skin++cms/cms/edition-/@@edit' % s.server,
            s.getLocation())
        transaction.begin()
        self.assertEquals('redirect', self.cms.type)

    def test_delete_page(self):
        s = self.selenium
        self.cms['xy'] = asm.cms.page.Page('htmlpage')
        edition = self.cms['xy'].editions.next()
        edition.title = u'A test page'
        intids = zope.component.getUtility(zope.intid.interfaces.IIntIds)
        xy_id = intids.getId(edition.page)
        transaction.commit()
        s.open(
            'http://mgr:mgrpw@%s/++skin++cms/cms/xy/edition-/@@edit' %
            s.server)
        s.click('css=.toggle-navigation')
        s.waitForElementPresent('css=#%s a' % xy_id)
        s.click('css=#delete-page')
        s.waitForVisible('css=#confirm-deletion')
        # XXX I'm waiting for this to break ...
        s.click('css=.ui-dialog-buttonpane button')
        s.waitForElementNotPresent('css=#%s a' % xy_id)
        transaction.begin()
        self.assertRaises(KeyError, self.cms.__getitem__, 'xy')

    def test_cant_delete_root(self):
        intids = zope.component.getUtility(zope.intid.interfaces.IIntIds)
        edition = self.cms.editions.next()
        edition.title = u'Foobar'
        transaction.commit()
        cms_id = intids.getId(edition.page)
        s = self.selenium
        s.refresh()
        s.waitForPageToLoad()
        # In this case we are on the root page and the root element so it is
        # selected and page deletion button should be disabled.
        s.click('css=.toggle-navigation')
        s.waitForElementPresent('css=#%s a' % cms_id)
        s.assertNotEditable("css=#delete-page")
        transaction.abort()
        # TODO test case where we click some non-root node and see that page
        # deletion button will be editable again.
