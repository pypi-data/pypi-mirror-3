# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok


class ICMSSkin(grok.IDefaultBrowserLayer):
    grok.skin('cms')


class IRetailBaseSkin(grok.IDefaultBrowserLayer):
    # The base skin doesn't register views for content
    # types to allow using viewlets.
    grok.skin('retailbase')


class IRetailSkin(IRetailBaseSkin):
    grok.skin('retail')
