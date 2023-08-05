import grok
from zope import component

from zope.security import checkPermission

from horae.core import utils

from horae.properties import interfaces


class Properties(grok.OrderedContainer):
    """ Base implementation of a property container
    """
    grok.baseclass()
    grok.implements(interfaces.IProperties)

    # To be defined in the subclass
    holder_interface = None
    interface = None
    default_property_interface = None

    def available(self, property, initial=None, editable=None, display=None):
        """ Whether the provided property is available
        """
        return ((initial is None or property.initial == initial) and
                (editable is None or property.editable == editable) and
                (display is None or property.display == display) and
                (property.permission is None or checkPermission(property.permission, self)))

    def filter(self, properties, initial=None, editable=None, display=None, ignore=[]):
        """ Filter a list of properties
        """
        filtered = []
        for property in properties:
            if not self.available(property, initial, editable, display) or property.id in ignore:
                continue
            filtered.append(property)
        return filtered

    def properties(self, initial=None, editable=None, display=None):
        """ Returns the available properties
        """
        parent = utils.findParentByInterface(self, self.holder_interface, 1)
        properties = self.filter(self.values(), initial, editable, display)
        if parent is not None:
            properties += self.filter(self.interface(parent).properties(), initial, editable, display, self)
        else:
            properties += self.filter(component.getAllUtilitiesRegisteredFor(self.default_property_interface), initial, editable, display, self)
        return sorted(properties, key=lambda property: property.order)

    def add_property(self, property):
        """ Adds a property
        """
        self[property.id] = property

    def del_property(self, id):
        """ Deletes the property with the specified id
        """
        del self[id]

    def get_property(self, id):
        """ Returns the property with the specified id
        """
        if not id in self:
            parent = utils.findParentByInterface(self, self.holder_interface, 1)
            if parent is not None:
                return self.interface(parent).get_property(id)
            else:
                return component.queryUtility(self.default_property_interface, name=id)
        return self[id]

    def fields(self, initial=None, editable=None, display=None):
        """ Iterator over the fields of the available properties
        """
        for property in self.properties(initial, editable, display):
            for field in property.fields():
                yield field


class GlobalProperties(Properties):
    """ Holds properties available for all objects
    """
    grok.implements(interfaces.IGlobalProperties)
    holder_interface = interfaces.IGlobalPropertiesHolder
    interface = interfaces.IGlobalProperties
    default_property_interface = interfaces.IDefaultGlobalProperty


@grok.adapter(interfaces.IGlobalPropertiesHolder)
@grok.implementer(interfaces.IGlobalProperties)
def global_properties_of_holder(holder):
    """ Returns a container for global properties if it does not yet
        exist one is created
    """
    if not 'global_properties' in holder:
        holder['global_properties'] = GlobalProperties()
    return holder['global_properties']


@grok.adapter(interfaces.IPropertied, name='global')
@grok.implementer(interfaces.IProperties)
def global_properties_for_propertied(propertied):
    """ Provides global properties for :py:class:`horae.properties.interfaces.IPropertied`
    """
    holder = utils.findParentByInterface(propertied, interfaces.IGlobalPropertiesHolder)
    return interfaces.IGlobalProperties(holder)


class ClientProperties(Properties):
    """ Holds properties for clients
    """
    grok.implements(interfaces.IClientProperties)
    holder_interface = interfaces.IClientPropertiesHolder
    interface = interfaces.IClientProperties
    default_property_interface = interfaces.IDefaultClientProperty


@grok.adapter(interfaces.IClientPropertiesHolder)
@grok.implementer(interfaces.IClientProperties)
def client_properties_of_holder(holder):
    """ Returns a container for client properties if it does not yet
        exist one is created
    """
    if not 'client_properties' in holder:
        holder['client_properties'] = ClientProperties()
    return holder['client_properties']


class ProjectProperties(Properties):
    """ Holds properties for projects
    """
    grok.implements(interfaces.IProjectProperties)
    holder_interface = interfaces.IProjectPropertiesHolder
    interface = interfaces.IProjectProperties
    default_property_interface = interfaces.IDefaultProjectProperty


@grok.adapter(interfaces.IProjectPropertiesHolder)
@grok.implementer(interfaces.IProjectProperties)
def project_properties_of_holder(holder):
    """ Returns a container for project properties if it does not yet
        exist one is created
    """
    if not 'project_properties' in holder:
        holder['project_properties'] = ProjectProperties()
    return holder['project_properties']


class MilestoneProperties(Properties):
    """ Holds properties for milestones
    """
    grok.implements(interfaces.IMilestoneProperties)
    holder_interface = interfaces.IMilestonePropertiesHolder
    interface = interfaces.IMilestoneProperties
    default_property_interface = interfaces.IDefaultMilestoneProperty


@grok.adapter(interfaces.IMilestonePropertiesHolder)
@grok.implementer(interfaces.IMilestoneProperties)
def milestone_properties_of_holder(holder):
    """ Returns a container for milestone properties if it does not yet
        exist one is created
    """
    if not 'milestone_properties' in holder:
        holder['milestone_properties'] = MilestoneProperties()
    return holder['milestone_properties']


class TicketProperties(Properties):
    """ Holds properties for tickets
    """
    grok.implements(interfaces.ITicketProperties)
    holder_interface = interfaces.ITicketPropertiesHolder
    interface = interfaces.ITicketProperties
    default_property_interface = interfaces.IDefaultTicketProperty


@grok.adapter(interfaces.ITicketPropertiesHolder)
@grok.implementer(interfaces.ITicketProperties)
def ticket_properties_of_holder(holder):
    """ Return a container for milestone properties if it does not yet
        exist one is created
    """
    if not 'ticket_properties' in holder:
        holder['ticket_properties'] = TicketProperties()
    return holder['ticket_properties']
