# Copyright (c) 2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.cms
import gocept.selenium.ztk
import os.path
import transaction
import zope.app.component.hooks
import zope.app.testing.functional


TestLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'TestLayer', allow_teardown=False)


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):

    layer = TestLayer

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        r = self.getRootFolder()
        r['cms'] = self.cms = asm.cms.cms.CMS()
        zope.app.component.hooks.setSite(self.cms)
        transaction.commit()

    def tearDown(self):
        zope.app.component.hooks.setSite(None)
        super(FunctionalTestCase, self).tearDown()


class SeleniumTestCase(gocept.selenium.ztk.TestCase):

    layer = gocept.selenium.ztk.Layer(TestLayer)

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        r = self.getRootFolder()
        r['cms'] = self.cms = asm.cms.cms.CMS()
        transaction.commit()
        zope.app.component.hooks.setSite(self.cms)
        self.selenium.open('http://mgr:mgrpw@%s/++skin++cms/cms' %
                           self.selenium.server)

    def tearDown(self):
        zope.app.component.hooks.setSite(None)
        super(SeleniumTestCase, self).tearDown()
