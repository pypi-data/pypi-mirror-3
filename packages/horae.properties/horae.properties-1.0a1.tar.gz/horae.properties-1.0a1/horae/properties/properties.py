import grok
import re
from datetime import datetime, timedelta

from persistent import Persistent
from zope import schema
from zope import component
from zope import interface
from zope.i18n import translate
from zope.site.hooks import getSite
from zope.formlib.widget import renderElement, CustomWidgetFactory
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.app.intid.interfaces import IIntIds
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from z3c.relationfield.interfaces import IHasRelations
from z3c.relationfield import RelationValue
from megrok.form import fields

from horae.core import utils
from horae.core.interfaces import ICurrencyFormatter
from horae.auth.utils import getUser, getGroup
from horae.auth.interfaces import IUserURL
from horae.layout.widgets import ObjectWidget
from horae.layout.widgets import ListSequenceWidget
from horae.timeaware.timeaware import DatetimeFieldProperty
from horae.autocomplete.fields import AutocompleteChoice

from horae.properties import _
from horae.properties import interfaces


class PropertyTypes(object):
    """ Provider for available properties
    """
    grok.implements(interfaces.IPropertyTypes)

    def __init__(self):
        self._types = []

    def add(self, type):
        if not interfaces.IProperty:
            raise ValueError(type)
        self._types.append(type)

    def types(self):
        """ Returns a list of available property types
        """
        return self._types

property_types = PropertyTypes()


def property_types_singleton():
    """ Returns the :py:class:`PropertyTypes` singleton
    """
    return property_types
grok.global_utility(property_types_singleton, interfaces.IPropertyTypes)


class Property(grok.Model):
    """ A definition of a property
    """
    grok.baseclass()

    id = schema.fieldproperty.FieldProperty(interfaces.IProperty['id'])
    name = schema.fieldproperty.FieldProperty(interfaces.IProperty['name'])
    description = schema.fieldproperty.FieldProperty(interfaces.IProperty['description'])
    required = schema.fieldproperty.FieldProperty(interfaces.IProperty['required'])
    initial = schema.fieldproperty.FieldProperty(interfaces.IProperty['initial'])
    editable = schema.fieldproperty.FieldProperty(interfaces.IProperty['editable'])
    order = schema.fieldproperty.FieldProperty(interfaces.IProperty['order'])
    display = schema.fieldproperty.FieldProperty(interfaces.IProperty['display'])
    remember = schema.fieldproperty.FieldProperty(interfaces.IProperty['remember'])
    searchable = schema.fieldproperty.FieldProperty(interfaces.IProperty['searchable'])
    complete = schema.fieldproperty.FieldProperty(interfaces.IProperty['complete'])
    offer = schema.fieldproperty.FieldProperty(interfaces.IProperty['offer'])

    customizable = True
    permission = None

    def _prepare_fields(self, fields):
        i = 0.0
        for field in fields:
            field.interface = interfaces.IPropertiesProxy
            field.property = self
            field.order = self.order + i
            interface.alsoProvides(field, interfaces.IPropertyField)
            i += 0.0001
        return fields

    def custom_widget(self, form_fields):
        """ Called after the form fields for the add or edit form of a property have been created
            may be used to add custom widgets to specific fields
        """
        pass

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        raise NotImplementedError(u'concrete classes must implement fields()')

    def field_names(self):
        """ Returns a list of field names provided by this property
        """
        return [self.id, ]

    def process(self, **data):
        """ Processes the input coming from the form and returns a new data dictionary
        """
        return data

    def apply(self, obj, **data):
        """ Applies the data to the obj
        """
        pass

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        return widget is not None and widget() or value

    def clone(self):
        """ Returns a copy of the property
        """
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.id = self.id
        clone.__name__ = clone.__parent__ = None
        return clone

    def validate(self, data, context):
        """ Validates the form data

            Returns a list of exceptions or an empty one if the data is valid
        """
        return []

    def empty(self, value):
        """ Decides whether the value provided is an empty value for this property type
        """
        return value is None


class BoolProperty(Property):
    """ A boolean property
    """
    grok.implements(interfaces.IBoolProperty)
    type = _(u'Boolean')
    default = schema.fieldproperty.FieldProperty(interfaces.IBoolProperty['default'])

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        return value and _(u'Yes') or _(u'No')

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.Bool(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default
            ),
        ])
property_types.add(BoolProperty)


class TextLineProperty(Property):
    """ A textline property
    """
    grok.implements(interfaces.ITextLineProperty)
    type = _(u'Text line')
    default = schema.fieldproperty.FieldProperty(interfaces.ITextLineProperty['default'])

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.TextLine(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default
            ),
        ])
property_types.add(TextLineProperty)


class TextProperty(Property):
    """ A text property
    """
    grok.implements(interfaces.ITextProperty)
    type = _(u'Text')
    default = schema.fieldproperty.FieldProperty(interfaces.ITextProperty['default'])

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.Text(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default
            ),
        ])
property_types.add(TextProperty)


class RichTextProperty(Property):
    """ A rich text property
    """
    grok.implements(interfaces.IRichTextProperty)
    type = _(u'Rich text')
    default = u''

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            fields.HTML(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default
            ),
        ])
property_types.add(RichTextProperty)


class ChoiceProperty(Property):
    """ A choice property
    """
    grok.implements(interfaces.IChoiceProperty)
    type = _(u'Choice')
    vocabulary = schema.fieldproperty.FieldProperty(interfaces.IChoiceProperty['vocabulary'])
    default = schema.fieldproperty.FieldProperty(interfaces.IChoiceProperty['default'])
    numbered = re.compile(r'^[0-9]+')

    def convertValue(self, value):
        numbered = self.numbered.match(value)
        if numbered is None:
            return value
        return int(numbered.group(0))

    def getVocabulary(self, context):
        """ Returns the vocabulary used by the field
        """
        terms = []
        for value in self.vocabulary:
            converted = self.convertValue(value)
            terms.append(schema.vocabulary.SimpleTerm(converted, converted, value))
        return schema.vocabulary.SimpleVocabulary(terms)

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if widget is not None:
            return widget()
        if not value:
            return value
        vocabulary = self.getVocabulary(context)
        if not value in vocabulary:
            return translate(_(u'${value} (value no longer in vocabulary)', mapping=dict(value=value)), context=request)
        term = vocabulary.getTerm(value)
        if ITitledTokenizedTerm.providedBy(term):
            return term.title
        return term.token

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.Choice(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.convertValue(self.default),
                vocabulary=self.getVocabulary(context)
            ),
        ])
property_types.add(ChoiceProperty)


class MultipleChoiceProperty(ChoiceProperty):
    """ A multiple choice property
    """

    def convertValue(self, value):
        converted = set([])
        if not value:
            return converted
        for val in value:
            converted.add(super(MultipleChoiceProperty, self).convertValue(val))
        return converted

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if widget is not None:
            return widget()
        if not value:
            return value
        return ', '.join([super(MultipleChoiceProperty, self).render(val, context, request, widget) for val in value])

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        vocab = self.getVocabulary(context)
        if not len(vocab):
            return []
        return self._prepare_fields([
            schema.Set(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.convertValue(self.default),
                value_type=schema.Choice(
                    vocabulary=vocab
                )
            ),
        ])
property_types.add(MultipleChoiceProperty)


class WeightedOption(Persistent):
    """ A weighted option
    """
    grok.implements(interfaces.IWeightedOption)
    name = schema.fieldproperty.FieldProperty(interfaces.IWeightedOption['name'])
    affects_sorting = schema.fieldproperty.FieldProperty(interfaces.IWeightedOption['weight'])

    def __init__(self, name=u'', weight=1):
        super(WeightedOption, self).__init__()
        self.name = name
        self.weight = weight


class WeightedChoiceProperty(ChoiceProperty):
    """ A choice property having weighted options
    """
    grok.implements(interfaces.IWeightedChoiceProperty)
    type = _(u'Weighted choice')
    vocabulary = schema.fieldproperty.FieldProperty(interfaces.IWeightedChoiceProperty['vocabulary'])
    affects_sorting = schema.fieldproperty.FieldProperty(interfaces.IWeightedChoiceProperty['affects_sorting'])

    def custom_widget(self, form_fields):
        """ Called after the form fields for the add or edit form of a property have been created
            may be used to add custom widgets to specific fields
        """
        form_fields['vocabulary'].custom_widget = CustomWidgetFactory(ListSequenceWidget, subwidget=CustomWidgetFactory(ObjectWidget, WeightedOption))

    def getVocabulary(self, context):
        """ Returns the vocabulary used by the field
        """
        terms = []
        for value in self.vocabulary:
            terms.append(schema.vocabulary.SimpleTerm(value.name, value.name, value.name))
        return schema.vocabulary.SimpleVocabulary(terms)
property_types.add(WeightedChoiceProperty)


class FloatProperty(Property):
    """ A float property
    """
    grok.implements(interfaces.IFloatProperty)
    type = _(u'Float')
    default = schema.fieldproperty.FieldProperty(interfaces.IFloatProperty['default'])
    min = schema.fieldproperty.FieldProperty(interfaces.IFloatProperty['min'])
    max = schema.fieldproperty.FieldProperty(interfaces.IFloatProperty['max'])

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if value is None:
            return value
        return utils.formatHours(value, request)

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.Float(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default,
                min=self.min,
                max=self.max
            ),
        ])
property_types.add(FloatProperty)


class PriceProperty(FloatProperty):
    """ A price property
    """
    grok.implements(interfaces.IPriceProperty)
    type = _(u'Price')

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if value is None:
            return value
        return component.getMultiAdapter((getSite(), request), interface=ICurrencyFormatter).format(value)
property_types.add(PriceProperty)


class UserProperty(Property):
    """ A user property
    """
    grok.implements(interfaces.IUserProperty)
    type = _(u'User')
    default = None

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if value is None:
            return value
        user = getUser(value)
        url = user and component.queryAdapter(user, interface=IUserURL) or None
        return user and (url and '<a href="%s">%s</a>' % (url(), user.name) or user.name) or value

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            AutocompleteChoice(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default,
                vocabulary='horae.auth.vocabulary.usernames'
            ),
        ])
property_types.add(UserProperty)


class UserRoleProperty(UserProperty):
    """ A user role property
    """
    grok.implements(interfaces.IUserRoleProperty)
    type = _(u'User role')
    role = None

    def apply(self, obj, **data):
        """ Applies the data to the obj
        """
        manager = IPrincipalRoleManager(obj)
        principals = manager.getPrincipalsForRole(self.role)
        for principal, setting in principals:
            manager.unsetRoleForPrincipal(self.role, principal)
        if self.id in data and data[self.id]:
            manager.assignRoleToPrincipal(self.role, data[self.id])
property_types.add(UserRoleProperty)


class GroupProperty(Property):
    """ A group property
    """
    grok.implements(interfaces.IGroupProperty)
    type = _(u'Group')
    default = None

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if value is None:
            return value
        user = getGroup(value)
        return user and user.name or value

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            AutocompleteChoice(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default,
                vocabulary='horae.auth.vocabulary.groupids'
            ),
        ])
property_types.add(GroupProperty)


class GroupRoleProperty(GroupProperty):
    """ A group role property
    """
    grok.implements(interfaces.IGroupRoleProperty)
    type = _(u'Group role')
    role = None

    def apply(self, obj, **data):
        """ Applies the data to the obj
        """
        manager = IPrincipalRoleManager(obj)
        principals = manager.getPrincipalsForRole(self.role)
        for principal, setting in principals:
            manager.unsetRoleForPrincipal(self.role, principal)
        if self.id in data and data[self.id]:
            manager.assignRoleToPrincipal(self.role, data[self.id])
property_types.add(GroupRoleProperty)


class DateTimeProperty(Property):
    """ A date time property
    """
    grok.implements(interfaces.IDateTimeProperty)
    type = _(u'Datetime')
    default = DatetimeFieldProperty(interfaces.IDateTimeProperty['default'])
    default_now = schema.fieldproperty.FieldProperty(interfaces.IDateTimeProperty['default_now'])

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.Datetime(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default_now and datetime.now() or self.default
            ),
        ])

    def process(self, **data):
        """ Processes the input coming from the form and returns a new data dictionary
        """
        if self.id in data and isinstance(data[self.id], datetime):
            data[self.id] = datetime(data[self.id].year, data[self.id].month, data[self.id].day, data[self.id].hour, data[self.id].minute)
        return data

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if not isinstance(value, datetime):
            return value
        if value:
            value = utils.formatDateTime(value, request)
        return value
property_types.add(DateTimeProperty)


class DateTimeRangeProperty(DateTimeProperty):
    """ A date time range property
    """
    grok.implements(interfaces.IDateTimeRangeProperty)
    type = _(u'Datetime range')
    name_end = schema.fieldproperty.FieldProperty(interfaces.IDateTimeRangeProperty['name_end'])
    description_end = schema.fieldproperty.FieldProperty(interfaces.IDateTimeRangeProperty['description_end'])
    required_end = schema.fieldproperty.FieldProperty(interfaces.IDateTimeRangeProperty['required_end'])
    default_diff = schema.fieldproperty.FieldProperty(interfaces.IDateTimeRangeProperty['default_diff'])
    hours = schema.fieldproperty.FieldProperty(interfaces.IDateTimeRangeProperty['hours'])

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        default_end = self.default_now and datetime.now() or self.default
        default_start = default_end is not None and default_end - timedelta(hours=float(self.default_diff)) or None
        fields = []
        if self.hours:
            fields.append(
                schema.Float(
                    __name__=self.id + '_hours',
                    title=_(u'Hours'),
                    required=False,
                    default=float(self.default_diff)
                )
            )
        fields.extend([
            schema.Datetime(
                __name__=self.id + '_start',
                title=self.name,
                description=self.description,
                required=self.required,
                default=default_start
            ),
            schema.Datetime(
                __name__=self.id + '_end',
                title=self.name_end,
                description=self.description_end,
                required=self.required_end,
                default=default_end
            ),
        ])
        return self._prepare_fields(fields)

    def field_names(self):
        """ Returns a list of field names provided by this property
        """
        return [self.id + '_start', self.id + '_end', ]

    def process(self, **data):
        """ Processes the input coming from the form and returns a new data dictionary
        """
        if self.id + '_hours' in data:
            del data[self.id + '_hours']
        if self.id + '_start' in data and isinstance(data[self.id + '_start'], datetime):
            data[self.id + '_start'] = datetime(data[self.id + '_start'].year, data[self.id + '_start'].month, data[self.id + '_start'].day, data[self.id + '_start'].hour, data[self.id + '_start'].minute)
        if self.id + '_end' in data and isinstance(data[self.id + '_end'], datetime):
            data[self.id + '_end'] = datetime(data[self.id + '_end'].year, data[self.id + '_end'].month, data[self.id + '_end'].day, data[self.id + '_end'].hour, data[self.id + '_end'].minute)
        return data

    def validate(self, data, context):
        """ Validates the form data

            Returns a list of exceptions or an empty one if the data is valid
        """
        if self.id + '_start' in data and \
           self.id + '_end' in data and \
           data[self.id + '_start'] is not None and \
           data[self.id + '_end'] is not None and \
           data[self.id + '_start'] > data[self.id + '_end']:
            return [interface.Invalid(_(u'${end_date} before ${start_date}', mapping={'end_date': self.name_end, 'start_date': self.name})), ]
        return []
property_types.add(DateTimeRangeProperty)


class MilestoneProperty(Property):
    """ A milestone property
    """
    grok.implements(interfaces.IMilestoneProperty)
    type = _(u'Milestone')
    default = schema.fieldproperty.FieldProperty(interfaces.IMilestoneProperty['default'])

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.Choice(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default,
                vocabulary='horae.properties.vocabulary.milestones'
            ),
        ])

    def apply(self, obj, **data):
        """ Applies the data to the obj
        """
        if not self.id in data or \
           not IHasRelations.providedBy(obj) or \
           not hasattr(obj, self.id + '_rel'):
            return
        milestone = data[self.id]
        if milestone is None:
            setattr(obj, self.id + '_rel', None)
            return
        intids = component.getUtility(IIntIds)
        setattr(obj, self.id + '_rel', RelationValue(intids.queryId(milestone)))

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if value is None and widget:
            if widget._renderedValueSet():
                value = widget._data
        if value is None:
            return super(MilestoneProperty, self).render(value, request, widget)
        return renderElement('a',
                             href=component.getMultiAdapter((value, request), name='absolute_url'),
                             title=value.description,
                             contents=widget is not None and widget() or value.name)


class FieldsProperty(Property):
    """ A fields property
    """
    grok.implements(interfaces.IFieldsProperty)
    type = _(u'Fields')

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            schema.Set(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=set(),
                value_type=schema.Choice(
                    vocabulary='horae.properties.vocabulary.fields'
                )
            ),
        ])

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if widget is not None:
            return widget()
        if value is None or not len(value):
            return None
        return ', '.join([v for v in iter(value)])
