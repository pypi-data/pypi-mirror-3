# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import asm.cms.cms
import asm.cmsui.interfaces
import grok
import hurry.query.query
import simplejson
import megrok.pagelet
import zope.component
import zope.index.text.parsetree

class Search(megrok.pagelet.Pagelet):

    grok.context(asm.cms.cms.CMS)
    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    def update(self):
        self.keyword = q = self.request.form.get('q', '')
        try:
            self.results = hurry.query.query.Query().searchResults(
                hurry.query.Text(('edition_catalog', 'body'), q))
        except zope.index.text.parsetree.ParseError, e:
            self.flash(e.message)
            self.results = []


class SearchBase(object):

    def update(self):
        self.keyword = q = self.request.form.get('q', '')

        try:
            results = hurry.query.query.Query().searchResults(
                hurry.query.Text(('edition_catalog', 'body'), q))
        except zope.index.text.parsetree.ParseError, e:
            self.flash(e.message)
            self.results = []
            return

        self.results = []
        for result in results:
            if result is asm.cms.edition.select_edition(result.page, self.request):
                self.results.append(result)


class PublicSearch(SearchBase, megrok.pagelet.Pagelet):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailSkin)
    grok.name('search')

    def sites(self):
        return asm.cms.interfaces.ISearchSites(self.application).sites


class PublicJsonSearch(SearchBase, grok.View):

    grok.context(asm.cms.interfaces.IEdition)
    grok.layer(asm.cmsui.interfaces.IRetailSkin)
    grok.name('search.json')

    def render(self):
        output = []
        for edition in self.results:
            preview = ""
            try:
                view = zope.component.getMultiAdapter(
                    (edition, self.request), name="searchpreview")
                preview = view()
            except LookupError:
                pass

            output.append({
                    'title': edition.title,
                    'url': self.url(edition),
                    'content': preview,
                    })

        return simplejson.dumps(output)


class OSDDEdition(grok.View):
    grok.context(asm.cms.interfaces.IEdition)
    grok.name("osdd.xml")
    grok.template("osdd")

    def title(self):
        return self.context.title


class OSDDCMS(grok.View):
    grok.context(asm.cms.interfaces.ICMS)
    grok.name("osdd.xml")
    grok.template("osdd")

    def title(self):
        edition = asm.cms.edition.select_edition(self.context, self.request)
        return edition.title + u" CMS"


class SelectSearchSites(asm.cmsui.form.EditForm):

    form_fields = grok.AutoFields(asm.cms.interfaces.ISearchSites)
    grok.context(asm.cms.cms.CMS)
