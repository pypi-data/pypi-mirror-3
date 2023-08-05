# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailSkin(grok.IDefaultBrowserLayer):
    grok.skin('retail')
