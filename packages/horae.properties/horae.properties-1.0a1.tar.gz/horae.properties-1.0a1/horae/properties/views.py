import grok
import os

from grokcore.chameleon.components import ChameleonPageTemplate
from zope import component
from zope.i18n import translate
from zope.formlib.widget import renderElement
from megrok import navigation

from horae.core import utils
from horae.core.interfaces import ITextIdManager
from horae.layout.interfaces import IActionsMenu, IViewsMenu, IContextualManageMenu
from horae.layout import layout
from horae.layout import _ as _l
from horae.auth.utils import getUser
from horae.auth.interfaces import IUserURL

from horae.properties import _
from horae.properties import interfaces

grok.templatedir('templates')


class DeletePropertied(layout.DeleteForm):
    """ Delete form of a propertied
    """
    grok.context(interfaces.IPropertied)
    grok.require('horae.Delete')
    grok.name('delete')
    navigation.menuitem(IActionsMenu, _(u'Delete'))

    def item_title(self):
        return getattr(self.context, 'name', self.context.id)

    def object_type(self):
        return interfaces.IObjectType(self.context, lambda: _l(u'Item'))()


class PropertiesOverview(layout.View):
    """ Overview of available property containers
    """
    grok.context(interfaces.IPropertiesHolder)
    grok.require('horae.Manage')
    grok.name('properties')
    navigation.menuitem(IContextualManageMenu, _(u'Properties'))

    def update(self):
        super(PropertiesOverview, self).update()
        self.properties = []
        if interfaces.IGlobalPropertiesHolder.providedBy(self.context):
            self.properties.append({'title': _(u'Global properties'),
                                    'description': _(u'Properties available for all objects'),
                                    'url': self.url(interfaces.IGlobalProperties(self.context))})
        if interfaces.IClientPropertiesHolder.providedBy(self.context):
            self.properties.append({'title': _(u'Client properties'),
                                    'description': _(u'Properties available for clients'),
                                    'url': self.url(interfaces.IClientProperties(self.context))})
        if interfaces.IProjectPropertiesHolder.providedBy(self.context):
            self.properties.append({'title': _(u'Project properties'),
                                    'description': _(u'Properties available for projects'),
                                    'url': self.url(interfaces.IProjectProperties(self.context))})
        if interfaces.IMilestonePropertiesHolder.providedBy(self.context):
            self.properties.append({'title': _(u'Milestone properties'),
                                    'description': _(u'Properties available for milestones'),
                                    'url': self.url(interfaces.IMilestoneProperties(self.context))})
        if interfaces.ITicketPropertiesHolder.providedBy(self.context):
            self.properties.append({'title': _(u'Ticket properties'),
                                    'description': _(u'Properties available for tickets'),
                                    'url': self.url(interfaces.ITicketProperties(self.context))})


class Properties(layout.View):
    """ Overview of properties
    """
    grok.context(interfaces.IProperties)
    grok.name('index')
    grok.require('horae.Manage')
    grok.template('properties')

    button_template = u'<a href="%(url)s" class="button button-discreet %(cls)s">%(label)s</a> '

    def label(self):
        if interfaces.IGlobalProperties.providedBy(self.context):
            return _(u'Global properties')
        if interfaces.IClientProperties.providedBy(self.context):
            return _(u'Client properties')
        if interfaces.IProjectProperties.providedBy(self.context):
            return _(u'Project properties')
        if interfaces.IMilestoneProperties.providedBy(self.context):
            return _(u'Milestone properties')
        if interfaces.ITicketProperties.providedBy(self.context):
            return _(u'Ticket properties')

    def get_table(self, properties):
        table = component.getMultiAdapter((self.context, self.request), name='table')
        table.page_size = None
        table.columns = [('name', _(u'Name')), ('description', _(u'Description')), ('type', _(u'Type')), ('actions', u'')]
        table.sortable = {}
        table.base_url = self.url(self.context)
        table.rows = properties
        return table()

    def update(self):
        super(Properties, self).update()
        self.back = self.url(self.context.__parent__) + '/properties'
        properties = self.context.properties()
        self.custom_properties = []
        self.inherited_properties = []
        for property in properties:
            item = {'name': property.name,
                    'description': property.description,
                    'type': property.type,
                    'actions': ''}
            if not interfaces.IDefaultProperty.providedBy(property) and property.__parent__ == self.context:
                item['actions'] = '<div class="button-group">%s</div>' % (
                                    (self.button_template % {'url': self.url(self.context) + '/edit-property?id=' + property.id,
                                                             'label': translate(_(u'Edit'), context=self.request),
                                                             'cls': ''}) + \
                                    (self.button_template % {'url': self.url(self.context) + '/delete-property?id=' + property.id,
                                                             'label': translate(_(u'Delete'), context=self.request),
                                                             'cls': 'button-destructive delete'}))
                self.custom_properties.append(item)
            else:
                if property.customizable:
                    item['actions'] = '<div class="button-group">%s</div>' % \
                                        self.button_template % {'url': self.url(self.context) + '/customize-property?id=' + property.id,
                                                                'label': translate(_(u'Customize'), context=self.request),
                                                                'cls': ''}
                self.inherited_properties.append(item)
        if self.custom_properties:
            self.custom_properties = self.get_table(self.custom_properties)
        if self.inherited_properties:
            self.inherited_properties = self.get_table(self.inherited_properties)
        normalizer = component.getUtility(ITextIdManager)
        types = component.getUtility(interfaces.IPropertyTypes).types()
        self.types = [dict(value=normalizer.normalize(type.type),
                           title=type.type) for type in types]


class PropertyFormMixin(object):
    """ Mixin class for forms of :py:class:`horae.properties.interfaces.IProperty`
    """

    def next_url(self, obj=None):
        return self.cancel_url()


class AddProperty(PropertyFormMixin, layout.AddForm):
    """ Add form for a :py:class:`horae.properties.interfaces.IProperty`
    """
    grok.context(interfaces.IProperties)
    grok.require('horae.Manage')
    grok.name('add-property')

    def __call__(self, type=None):
        self.type = self._findType(type)
        if self.type is not None:
            self.form_fields = grok.AutoFields(self.type).omit('id')
            self.type().custom_widget(self.form_fields)
            normalizer = component.getUtility(ITextIdManager)
            self.additional = renderElement('input',
                                            type='hidden',
                                            name='type',
                                            value=normalizer.normalize(self.type.type))
        else:
            self.redirect(self.cancel_url())
        return super(AddProperty, self).__call__()

    def _findType(self, type):
        if type is None:
            return None
        normalizer = component.getUtility(ITextIdManager)
        types = component.getUtility(interfaces.IPropertyTypes).types()
        for t in types:
            if normalizer.normalize(t.type) == type:
                return t

    def object_type(self):
        return self.type.type

    def create(self, **data):
        property = self.type()
        property.id = component.getUtility(ITextIdManager).idFromName(self.context, data['name'])
        return property

    def add(self, obj):
        self.context.add_property(obj)


class EditProperty(PropertyFormMixin, layout.EditForm):
    """ Edit form for a :py:class:`horae.properties.interfaces.IProperty`
    """
    grok.context(interfaces.IProperties)
    grok.require('horae.Manage')
    grok.name('edit-property')

    def __call__(self, id=None):
        self.property = self.context.get_property(id)
        if self.property is not None:
            self.form_fields = grok.AutoFields(self.property.__class__).omit('id')
            self.property.custom_widget(self.form_fields)
            self.additional = renderElement('input',
                                            type='hidden',
                                            name='id',
                                            value=self.property.id)
        else:
            self.redirect(self.cancel_url())
        return super(EditProperty, self).__call__()

    def object_type(self):
        return self.property.type

    def setUpWidgets(self, ignore_request=False):
        self.context, context = self.property, self.context
        super(EditProperty, self).setUpWidgets(ignore_request)
        self.context = context

    def apply(self, **data):
        self.applyData(self.context, **data)


class CustomizeProperty(PropertyFormMixin, layout.AddForm):
    """ Customization view for an existing
        :py:class:`horae.properties.interfaces.IProperty`
    """
    grok.context(interfaces.IProperties)
    grok.require('horae.Manage')
    grok.name('customize-property')

    def __call__(self, id=None):
        self.property = self.context.get_property(id)
        if self.property is None:
            self.redirect(self.cancel_url())
            return ''
        self.form_fields = grok.AutoFields(self.property.__class__).omit('id')
        self.property.custom_widget(self.form_fields)
        self.additional = renderElement('input',
                                        type='hidden',
                                        name='id',
                                        value=self.property.id)
        return super(CustomizeProperty, self).__call__()

    def object_type(self):
        return self.property.type

    def create(self, **data):
        return self.property.clone()

    def setUpWidgets(self, ignore_request=False):
        super(CustomizeProperty, self).setUpWidgets(ignore_request)
        for field in self.form_fields:
            name = field.field.__name__
            if ignore_request or not self.widgets[name].hasInput():
                self.widgets[name].setRenderedValue(getattr(self.property, name, None))

    def add(self, obj):
        self.context.add_property(obj)


class DeleteProperty(PropertyFormMixin, layout.DeleteForm):
    """ Delete form for a :py:class:`horae.properties.interfaces.IProperty`
    """
    grok.context(interfaces.IProperties)
    grok.require('horae.Manage')
    grok.name('delete-property')

    def __call__(self, id=None):
        self.property = self.context.get_property(id)
        if self.property is not None:
            self.additional = renderElement('input',
                                            type='hidden',
                                            name='id',
                                            value=self.property.id)
        else:
            self.redirect(self.cancel_url())
        return super(DeleteProperty, self).__call__()

    def object_type(self):
        return self.property.type

    def item_title(self):
        return self.property.name

    def delete(self):
        self.context.del_property(self.property.id)


class PropertiedFormMixin(object):
    """ Mix in class for forms of :py:class:`horae.properties.interfaces.IPropertied`
    """
    # To be provided by subclass
    interfaces = (interfaces.IGlobalPropertiesHolder, interfaces.IGlobalProperties)
    initial = None
    editable = None
    display = True

    def completed(self, context):
        return interfaces.IComplete(context, lambda: False)()

    def offer(self, context):
        return interfaces.IOffer(context, lambda: False)()

    def property_fields(self, context=None):
        if context is None:
            context = self.context
        completed = self.completed(context)
        offer = self.offer(context)
        ifaces = [self.interfaces, PropertiedFormMixin.interfaces]
        fields = {}
        seen = []
        self.properties = []
        self.field_map = {}
        for iface_holder, iface in ifaces:
            holder = utils.findParentByInterface(context, iface_holder)
            if holder is None:
                continue
            container = iface(holder)
            properties = container.properties()
            for property in properties:
                if property.id in seen:
                    continue
                seen.append(property.id)
                if not self.display and ((not property.complete and completed) or (not property.offer and offer)):
                    continue
                self.properties.append(property)
                available = container.available(property, self.initial, self.editable, self.display)
                if available:
                    for field in property.fields(context):
                        if available:
                            fields[field.__name__] = field
                        self.field_map[field.__name__] = field
        return fields

    def setUpWidgets(self, ignore_request=False):
        super(PropertiedFormMixin, self).setUpWidgets(ignore_request)
        for property in self.properties:
            if property.remember:
                continue
            for field in property.field_names():
                if self.widgets.get(field) is None:
                    continue
                if not self.widgets[field].hasInput():
                    self.widgets[field].setRenderedValue(None)

    def validate(self, action, data):
        errors = super(PropertiedFormMixin, self).validate(action, data)
        for property in self.properties:
            errors += property.validate(data, self.context)
        return errors

    def update(self):
        fields = self.property_fields()
        super(PropertiedFormMixin, self).update()
        for form_field in self.form_fields:
            field = form_field.field
            fields[field.__name__] = field
        self.form_fields = grok.Fields(**fields)

    def new_change(self, obj):
        obj.new_change()

    def process_properties(self, **data):
        for property in self.properties:
            data = property.process(**data)
        return data

    def apply_properties(self, obj, **data):
        for property in self.properties:
            property.apply(obj, **data)


class PropertiedAddForm(PropertiedFormMixin, layout.AddForm):
    """ Add form for :py:class:`horae.properties.interfaces.IPropertied`
    """
    grok.baseclass()
    # To be provided by subclass
    factory = None
    container_interface = None
    initial = True
    editable = None
    display = None

    def completed(self, context):
        return False

    def apply(self, obj, **data):
        interfaces.IPropertied(obj).new_change()
        data = self.process_properties(**data)
        self.apply_properties(obj, **data)
        super(PropertiedAddForm, self).apply(obj, **data)

    def create(self, **data):
        obj = self.factory()
        return obj

    def add(self, obj):
        container = self.context
        while self.container_interface(container, None) is None:
            container = container.__parent__
        self.container_interface(container).add_object(obj)


class PropertiedEditForm(PropertiedFormMixin, layout.EditForm):
    """ Edit form for :py:class:`horae.properties.interfaces.IPropertied`
    """
    grok.baseclass()
    initial = None
    editable = True
    display = None

    def apply(self, **data):
        interfaces.IPropertied(self.context).new_change()
        data = self.process_properties(**data)
        self.apply_properties(self.context, **data)
        super(PropertiedEditForm, self).apply(**data)
        self.call_extenders('apply', obj=self.context, data=data)


class PropertyDisplayWidget(object):
    """ Display widget of a :py:class:`horae.properties.interfaces.IProperty`
    """

    def __init__(self, property, value, context, request, widget=None, cssClass=None):
        self._property = property
        self._value = value
        self._request = request
        self._widget = widget
        self._context = context
        self.prefix = widget is not None and widget._prefix or ''
        self.name = self.prefix + property.id
        self.label = property.name
        self.hint = property.description
        self.visible = True
        self.order = property.order
        self.cssClass = cssClass

    def __call__(self):
        if self._property.empty(self._value):
            return u''
        rendered = self._property.render(self._value, self._context, self._request, self._widget)
        if self.cssClass is not None:
            rendered = '<span class="%s">%s</span>' % (self.cssClass, rendered)
        return rendered


class PropertiedDisplayForm(PropertiedFormMixin, layout.DisplayForm):
    """ Display form for :py:class:`horae.properties.interfaces.IPropertied`
    """
    grok.baseclass()

    def setUpWidgets(self, ignore_request=False):
        super(PropertiedDisplayForm, self).setUpWidgets(ignore_request)
        property_map = dict([(property.id, property) for property in self.properties])
        new = []
        for widget in self.widgets:
            id = widget.name[len(widget._prefix):]
            if id in property_map:
                property = property_map[id]
                widget = PropertyDisplayWidget(property, interfaces.IPropertied(self.context).get_property(id), interfaces.IPropertied(self.context), self.request, widget)
            if not widget():
                continue
            new.append(widget)
        self.widgets = new
        providers = component.getAdapters((self.context,), interfaces.IPropertiedDisplayWidgetsProvider)
        for name, provider in providers:
            self.widgets = provider.widgets(self.widgets, self.request)
        self.widgets.sort(key=lambda x: getattr(x, 'order', 1))


class History(PropertiedDisplayForm):
    """ History of a :py:class:`horae.properties.interfaces.IPropertied`
    """
    grok.baseclass()
    grok.require('horae.ViewHistory')
    grok.template('history')
    template = ChameleonPageTemplate(os.path.join('templates', 'history.cpt'))
    grok.name('history')
    navigation.menuitem(IViewsMenu, _(u'History'))

    def __call__(self, change=None, previous=None, **kw):
        self.change = change
        self.previous = previous
        return super(History, self).__call__(**kw)

    def update(self):
        super(History, self).update()
        self.changes = []
        previous = None
        if self.change is None:
            previous = {}
            propertied = interfaces.IPropertied(self.context)
            changelog = propertied.changelog()
        else:
            changelog = [self.change, ]
        if self.previous is not None:
            previous = self.previous
        providers = [provider for name, provider in component.getAdapters((self.context,), interfaces.IHistoryPropertiesProvider)]
        for change in changelog:
            if previous is None:
                previous = dict(change.properties())
                continue
            creator = getUser(change.creator)
            item = {'id': change.id,
                    'user': creator is not None and creator.name or change.creator,
                    'user_url': creator is not None and IUserURL(creator, lambda: None)() or None,
                    'date': utils.formatDateTime(change.creation_date, self.request, ('dateTime', 'short')),
                    'name': change.get_property('name'),
                    'description': change.get_property('description'),
                    'title': change.get_property('title'),
                    'comment': change.get_property('comment'),
                    'workexpense': None,
                    'properties': []
                    }
            diff = {}
            for id, value in change.properties():
                field = id in self.field_map and self.field_map[id] or None
                if not field or not field.property.display:
                    continue
                if field and (not field.property.empty(value) or not field.property.empty(previous.get(id, None))):
                    if not field.property.id in diff:
                        diff[field.property.id] = 0.0
                    item['properties'].append({'name': field.title,
                                               'order': field.property.order + diff[field.property.id],
                                               'value': field.property.render(value, self.context, self.request),
                                               'previous': not field.property.empty(previous.get(id, None)) and field.property.render(previous.get(id, None), self.context, self.request) or None})
                    diff[field.property.id] += 0.1
            item['properties'].sort(key=lambda x: x['order'])
            for provider in providers:
                item['properties'] = provider.properties(change, item['properties'], self.request)
            previous.update(dict(change.properties()))
            if item['title'] or item['comment'] or item['name'] or item['description'] or item['properties']:
                self.changes.append(item)
        self.call_extenders('post_update')
