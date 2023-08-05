# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cmsui.testing


class ImportSelenium(asm.cmsui.testing.SeleniumTestCase):

    def test_import_form_available(self):
        s = self.selenium
        s.click('css=.toggle-navigation')
        s.click("xpath=//h3[contains(text(),'Tools')]/following-sibling::div[@class='opener']")
        s.assertVisible("xpath=//button[contains(text(), 'Import content')]")
        s.clickAndWait("xpath=//button[contains(text(), 'Import content')]")
