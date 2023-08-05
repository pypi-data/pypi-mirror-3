# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

# See also LICENSE.txt

import asm.cmsui.testing
import asm.cms.page
import transaction
import ZODB.blob


class Asset(asm.cmsui.testing.SeleniumTestCase):

    def setUp(self):
        super(Asset, self).setUp()
        self.cms['asset'] = asset = asm.cms.page.Page('asset')
        transaction.commit()
        self.selenium.open('http://%s/++skin++cms/cms/asset/edition-/@@edit' %
                           self.selenium.server)

    def test_asset_download_button_hidden_if_no_content(self):
        self.selenium.assertElementNotPresent(
            'xpath=//input[@type="button" and @value="Download"]')

    def test_asset_download_button(self):
        self.cms['asset'].editions.next().content = ZODB.blob.Blob()
        transaction.commit()

        s = self.selenium
        s.open('http://%s/++skin++cms/cms/asset/edition-/@@edit' % s.server)
        s.click('xpath=//input[@type="button" and @value="Download"]')
        self.assertEquals(
            'http://%s/++skin++cms/cms/asset/edition-/@@edit' % s.server
            ,s.getLocation())
