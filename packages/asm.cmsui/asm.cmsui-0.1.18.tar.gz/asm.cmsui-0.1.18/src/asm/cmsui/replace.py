# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import megrok.pagelet
import grok
import asm.cms.cms
import asm.cmsui.interfaces
import asm.cmsui.base
import zope.interface

grok.context(asm.cms.cms.CMS)

class SearchAndReplace(megrok.pagelet.Pagelet):
    """Present the user a form to allow entering search and replace terms."""

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')


class ReplacePreview(megrok.pagelet.Pagelet):
    """Given a users search and replace terms show a list of all matches."""

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.search = self.request.form.get('search', '')

        self.found = 0
        self.results = []
        pages = [self.application]
        while pages:
            page = pages.pop()
            pages.extend(page.subpages)
            for edition in page.editions:
                try:
                    replace = asm.cms.interfaces.IReplaceSupport(edition)
                except TypeError:
                    continue
                occurrences = replace.search(self.search)
                self.found += len(occurrences)
                if occurrences:
                    self.results.append(
                        {'edition': edition,
                         'occurrences': occurrences})


class Replace(megrok.pagelet.Pagelet):
    """Perform a replace operation given a users search and replace terms and
    a list of matches. Then display the remaining occurrences."""

    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.search = self.request.form.get('search', '')
        self.replace = self.request.form.get('replace')
        self.replaced = 0
        replace_cache = {}

        ids = zope.component.getUtility(zope.intid.interfaces.IIntIds)
        occurrences = self.request.form.get('occurrences')
        if isinstance(occurrences, basestring):
            occurrences = [occurrences]
        for occurrence_id in occurrences:
            id, _, _, _ = occurrence_id.split('-')
            if id not in replace_cache:
                edition = ids.getObject(int(id))
                replace = asm.cms.interfaces.IReplaceSupport(edition)
                replace_cache[id] = replace.search(self.search)
            occurrences = replace_cache[id]
            for candidate in occurrences:
                if candidate.id == occurrence_id:
                    candidate.replace(self.replace)
                    self.replaced += 1

    def render(self):
        self.flash('Replaced %s occurrences.' % self.replaced)
        self.redirect(self.url(self.context, 'searchandreplace'))


class ReplaceActions(grok.Viewlet):

    grok.template('actions')
    grok.viewletmanager(asm.cmsui.base.NavigationToolActions)
    grok.context(zope.interface.Interface)
