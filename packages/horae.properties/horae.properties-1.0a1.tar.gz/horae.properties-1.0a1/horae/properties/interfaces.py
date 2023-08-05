from zope import interface
from zope import schema
from zope.schema.interfaces import IField
from z3c.relationfield.interfaces import IHasRelations

from horae.core import interfaces
from horae.lifecycle.interfaces import ILifecycleAware

from horae.properties import _


class IProperties(interface.Interface):
    """ Property container
    """

    def available(property, initial=None, editable=None, display=None):
        """ Whether the provided property is available
        """

    def filter(properties, initial=None, editable=None, display=None, ignore=[]):
        """ Filter a list of properties
        """

    def properties(initial=None, editable=None, display=None):
        """ Returns the available properties
        """

    def add_property(property):
        """ Adds a property
        """

    def del_property(id):
        """ Deletes the property with the specified id
        """

    def get_property(id):
        """ Returns the property with the specified id
        """

    def fields(initial=None, editable=None, display=None):
        """ Iterator over the fields of the available properties
        """


class IPropertiesHolder(interface.Interface):
    """ Marker interface for objects holding properties
    """


class IGlobalProperties(IProperties):
    """ Holds properties available for all objects
    """


class IClientProperties(IProperties):
    """ Holds properties for clients
    """


class IProjectProperties(IProperties):
    """ Holds properties for projects
    """


class IMilestoneProperties(IProperties):
    """ Holds properties for milestones
    """


class ITicketProperties(IProperties):
    """ Holds properties for tickets
    """


class IGlobalPropertiesHolder(IPropertiesHolder):
    """ Marker interface for objects holding global properties
    """


class IClientPropertiesHolder(IPropertiesHolder):
    """ Marker interface for objects holding client properties
    """


class IProjectPropertiesHolder(IPropertiesHolder):
    """ Marker interface for objects holding project properties
    """


class IMilestonePropertiesHolder(IPropertiesHolder):
    """ Marker interface for objects holding milestone properties
    """


class ITicketPropertiesHolder(IPropertiesHolder):
    """ Marker interface for objects holding ticket properties
    """


class IPropertyTypes(interface.Interface):
    """ Provider for available property types
    """

    def types():
        """ Returns a list of available property types
        """


class IPropertyField(IField):
    """ A field of a property
    """

    property = interface.Attribute('property', 'The property this field belongs to')


class IProperty(interfaces.ITextId):
    """ A property
    """

    type = interface.Attribute('type',
        """ Type of property
        """
    )

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )

    required = schema.Bool(
        title=_(u'Required'),
        required=False,
        default=False
    )

    initial = schema.Bool(
        title=_(u'Initial'),
        description=_(u'Whether a property is editable while creating an object'),
        required=False,
        default=True
    )

    editable = schema.Bool(
        title=_(u'Editable'),
        description=_(u'Whether a property is editable on subsequent edits'),
        required=False,
        default=True
    )

    order = schema.Int(
        title=_(u'Order'),
        description=_(u'An integer which defines the order of the different properties'),
        required=True,
        default=1
    )

    display = schema.Bool(
        title=_(u'Display this property in the view of the object'),
        required=False,
        default=True
    )

    remember = schema.Bool(
        title=_(u'Remember the properties value for subsequent edits'),
        required=False,
        default=True
    )

    searchable = schema.Bool(
        title=_(u'Whether users may search for values of this field'),
        required=False,
        default=True
    )

    complete = schema.Bool(
        title=_(u'Whether this field is available for objects having a completed state'),
        required=False,
        default=True
    )

    offer = schema.Bool(
        title=_(u'Whether this field is available for objects having an offer state'),
        required=False,
        default=True
    )

    customizable = interface.Attribute('customizable')
    permission = interface.Attribute('permission')

    def custom_widget(form_fields):
        """ Called after the form fields for the add or edit form of a property have been created
            may be used to add custom widgets to specific fields
        """

    def fields(context):
        """ Returns a list of fields (IPropertyField)
        """

    def field_names():
        """ Returns a list of field names provided by this property
        """

    def process(**data):
        """ Processes the input coming from the form and returns a new data dictionary
        """

    def apply(obj, **data):
        """ Applies the data to the obj
        """

    def render(value, context, request, widget=None):
        """ Returns the rendered value
        """

    def clone():
        """ Returns a copy of the property
        """

    def validate(data, context):
        """ Validates the form data

            Returns a list of exceptions or an empty one if the data is valid
        """

    def empty(value):
        """ Decides whether the value provided is an empty value for this property type
        """


class IDefaultProperty(interface.Interface):
    """ Marker interface for default undeletable properties
    """


class IDefaultGlobalProperty(IDefaultProperty):
    """ Marker interface for default undeletable global properties
    """


class IDefaultClientProperty(IDefaultProperty):
    """ Marker interface for default undeletable client properties
    """


class IDefaultProjectProperty(IDefaultProperty):
    """ Marker interface for default undeletable project properties
    """


class IDefaultMilestoneProperty(IDefaultProperty):
    """ Marker interface for default undeletable global properties
    """


class IDefaultTicketProperty(IDefaultProperty):
    """ Marker interface for default undeletable ticket properties
    """


class IBoolProperty(IProperty):
    """ A boolean property
    """

    default = schema.Bool(
        title=_(u'Default value'),
        required=False
    )


class ITextLineProperty(IProperty):
    """ A textline property
    """

    default = schema.TextLine(
        title=_(u'Default value'),
        required=False
    )


class ITextProperty(IProperty):
    """ A text property
    """

    default = schema.Text(
        title=_(u'Default value'),
        required=False
    )


class IRichTextProperty(IProperty):
    """ A rich text property
    """


class IChoiceProperty(IProperty):
    """ A choice property
    """

    vocabulary = schema.List(
        title=_(u'Options'),
        description=_(u'Specify the available options'),
        required=True,
        value_type=schema.TextLine()
    )

    default = schema.TextLine(
        title=_(u'Default value'),
        required=False
    )

    def getVocabulary(context):
        """ Returns the vocabulary used by the field
        """

    @interface.invariant
    def defaultInVocabulary(choice_property):
        if not choice_property.default in choice_property.vocabulary:
            raise interface.Invalid(_(u'Default value not part of the options'))


class IMultipleChoiceProperty(IChoiceProperty):
    """ A multiple choice property
    """

    default = schema.List(
        title=_(u'Default value'),
        required=False,
        value_type=schema.TextLine()
    )

    @interface.invariant
    def defaultInVocabulary(multiple_choice_property):
        for default in multiple_choice_property.default:
            if not default in multiple_choice_property.vocabulary:
                raise interface.Invalid(_(u'Default value not part of the options'))


class IWeightedOption(interface.Interface):
    """ A weighted option
    """

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )

    weight = schema.Int(
        title=_(u'Weight'),
        required=True,
        default=1
    )


class IWeightedChoiceProperty(IChoiceProperty):
    """ A choice property having weighted options
    """

    vocabulary = schema.List(
        title=_(u'Options'),
        description=_(u'Specify the available options'),
        required=True,
        value_type=schema.Object(
            schema=IWeightedOption
        )
    )

    affects_sorting = schema.Bool(
        title=_(u'Affects sorting'),
        description=_(u'Whether this property affects sorting of the object or not')
    )

    @interface.invariant
    def defaultInVocabulary(weighted_choice_property):
        if not weighted_choice_property.default in [option.name for option in weighted_choice_property.vocabulary]:
            raise interface.Invalid(_(u'Default value not part of the options'))


class IFloatProperty(IProperty):
    """ A float property
    """

    default = schema.Float(
        title=_(u'Default value'),
        required=False
    )

    min = schema.Float(
        title=_(u'Minimum value'),
        required=False
    )

    max = schema.Float(
        title=_(u'Maximum value'),
        required=False
    )


class IPriceProperty(IFloatProperty):
    """ A price property
    """


class IUserProperty(IProperty):
    """ A user property
    """

    default = schema.Choice(
        title=_(u'Default value'),
        required=False,
        vocabulary='horae.auth.vocabulary.usernames'
    )


class IUserRoleProperty(IUserProperty):
    """ A user role property
    """

    role = schema.Choice(
        title=_(u'Role'),
        required=True,
        vocabulary='horae.auth.vocabulary.selectableroles'
    )


class IGroupProperty(IProperty):
    """ A group property
    """

    default = schema.Choice(
        title=_(u'Default value'),
        required=False,
        vocabulary='horae.auth.vocabulary.groupids'
    )


class IGroupRoleProperty(IGroupProperty):
    """ A group role property
    """

    role = schema.Choice(
        title=_(u'Role'),
        required=True,
        vocabulary='horae.auth.vocabulary.selectableroles'
    )


class IDateTimeProperty(IProperty):
    """ A date time property
    """

    default = schema.Datetime(
        title=_(u'Default value'),
        required=False
    )

    default_now = schema.Bool(
        title=_(u'Defaults to the date and time when viewed'),
        required=False,
        default=True
    )


class IDateTimeRangeProperty(IDateTimeProperty):
    """ A date time range property
    """

    name = schema.TextLine(
        title=_(u'Name (start date)'),
        required=True
    )

    description = schema.Text(
        title=_(u'Description (start date)'),
        required=False
    )

    required = schema.Bool(
        title=_(u'Required (start date)'),
        required=False
    )

    name_end = schema.TextLine(
        title=_(u'Name (end date)'),
        required=True
    )

    description_end = schema.Text(
        title=_(u'Description (end date)'),
        required=False
    )

    required_end = schema.Bool(
        title=_(u'Required (end date)'),
        required=False,
        default=False
    )

    default_diff = schema.Float(
        title=_(u'The default difference (in hours) between start and end date'),
        required=False,
        default=0.0
    )

    hours = schema.Bool(
        title=_(u'Show an additional hours field representing the range in hours'),
        required=False,
        default=False
    )


class IMilestoneProperty(IProperty):
    """ A milestone property
    """

    default = schema.Choice(
        title=_(u'Default value'),
        required=False,
        vocabulary='horae.properties.vocabulary.milestones'
    )


class IFieldsProperty(IProperty):
    """ A fields property
    """


class IPropertied(interface.Interface):
    """ An object storing dynamic properties and providing a history over them
    """

    def properties():
        """ Iterator over the available properties (IProperty)
        """

    def find_property(id):
        """ Trys to find and return the property having the specified id
        """

    def new_change():
        """ Starts a new property change and returns it
        """

    def get_property(id, default=None):
        """ Return the specific property value
        """

    def set_property(id, value):
        """ Sets a property on the currently active property change
        """

    def changelog():
        """ Iterator over the history of property changes
        """

    def current():
        """ Returns the current property change
        """


class IPropertiesProxy(interface.Interface):
    """ Proxy around IPropertied
    """

    def __getattr__(name):
        """ Returns the current property value
        """

    def __setattr__(name, value):
        """ Sets the value to the current property change
        """


class IPropertyChange(interfaces.IIntId, ILifecycleAware, IHasRelations):
    """ A change of multiple properties
    """

    def get_property(name, default=None):
        """ Returns the value of the specified property
        """

    def set_property(name, value):
        """ Sets a property to be changed
        """

    def properties():
        """ Iterator over the changed properties (name, value)
        """


class IPropertiedDisplayWidgetsProvider(interface.Interface):
    """ An adapter modifying and/or extending the widgets of a propertieds display view
    """

    def widgets(widgets, request):
        """ Returns a modified or extended list of widgets to be displayed
        """


class IHistoryPropertiesProvider(interface.Interface):
    """ An adapter providing properties for the history view
    """

    def properties(change, properties, request):
        """ Returns a modified or extended list of properties for the provided property change
        """


class IComplete(interface.Interface):
    """ Adapter to determine whether an object has been completed or not
    """

    def __call__():
        """ Returns whether the object has been completed or not
        """


class IOffer(interface.Interface):
    """ Adapter to determine whether an object is in the offer phase or not
    """

    def __call__():
        """ Returns whether the object is in the offer phase or not
        """


class IObjectType(interface.Interface):
    """ Adapter to define the user readable object type
    """

    def __call__():
        """ Returns the user readable object type
        """
