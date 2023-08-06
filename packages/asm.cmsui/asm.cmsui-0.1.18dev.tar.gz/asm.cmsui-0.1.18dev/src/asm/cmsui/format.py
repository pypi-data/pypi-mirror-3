# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grok
import datetime


class DateFormat(grok.View):

    grok.context(datetime.datetime)
    grok.name('format')

    def render(self):
        # XXX L10N or simple 'XXX time ago'
        return self.context.strftime('%d.%m.%Y %H:%M')


class NoneFormat(grok.View):
    grok.name('format')
    grok.context(None.__class__)

    def render(self):
        return ''
