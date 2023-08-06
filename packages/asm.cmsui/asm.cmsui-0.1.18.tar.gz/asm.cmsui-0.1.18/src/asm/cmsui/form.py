# Copyright (c) 2008-2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import asm.cmsui.interfaces
import grok
import megrok.pagelet
import os.path
import zope.app.container.interfaces
import zope.event
import zope.lifecycleevent
import zope.traversing.api


class CMSForm(object):

    grok.require('asm.cms.EditContent')
    grok.layer(asm.cmsui.interfaces.ICMSSkin)
    template = grok.PageTemplateFile(os.path.join("templates", "form.pt"))

    def __init__(self, context, request):
        super(CMSForm, self).__init__(context, request)
        self.group_info = {}

    def setUpWidgets(self, ignore_request=False):
        super(CMSForm, self).setUpWidgets(ignore_request)
        self.grouped_widgets = {}
        self.main_widgets = []
        for widget in self.widgets:
            group = getattr(self.form_fields[widget.context.__name__],
                            'location', None)
            if group is None:
                self.main_widgets.append(widget)
            else:
                group = self.grouped_widgets.setdefault(group, [])
                group.append(widget)


class Form(CMSForm, megrok.pagelet.component.FormPageletMixin, grok.Form):

    grok.baseclass()


class AddForm(CMSForm, megrok.pagelet.component.FormPageletMixin,
              grok.AddForm):

    grok.baseclass()

    # Needs to be set by the child class
    factory = None

    @grok.action("Add")
    def createAndAdd(self, **data):
        obj = self.create(**data)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.applyData(obj, **data)
        self.add(obj)
        self.redirect(self.url(self.target))

    def add(self, obj):
        name = self.chooseName(obj)
        self.context[name] = obj

    def create(self, **data):
        return self.factory()

    def chooseName(self, obj):
        chooser = zope.app.container.interfaces.INameChooser(self.context)
        return chooser.chooseName('', obj)

    @property
    def form_fields(self):
        return grok.AutoFields(self.factory)


class EditForm(CMSForm, megrok.pagelet.component.FormPageletMixin,
               grok.EditForm):

    grok.baseclass()

    def post_process(self):
        pass

    @grok.action("Save")
    def handle_edit_action(self, **data):
        super(EditForm, self).handle_edit_action.success(data)
        self.post_process()
        if self.errors:
            return
        self.flash(self.status)
        self.redirect(self.url(self.context, '@@' + self.__name__))
        # A hack to avoid rendering inspite of redirect.
        self.layout = lambda: ''


class EditionEditForm(EditForm):

    grok.baseclass()
    grok.name('edit')

    @property
    def label(self):
        return u'Edit %s' % self.context.page.type

    @property
    def form_fields(self):
        fields = self.main_fields
        fields += zope.formlib.form.FormFields(
            asm.cms.interfaces.IEdition).select('tags')
        fields['tags'].location = 'Tags'
        self.group_info['Tags'] = self.context.tags
        for schema in zope.component.subscribers(
                (self.context,),
                asm.cms.interfaces.IAdditionalSchema):
            self.group_info[schema.getTaggedValue('label')] = \
                schema.queryTaggedValue('description', '')
            add_fields = list(grok.AutoFields(schema))
            for field in add_fields:
                field.location = schema.getTaggedValue('label')
            fields += zope.formlib.form.FormFields(*add_fields)
        return fields
