import grok

from zope import component, schema
from zope.security import checkPermission

from BTrees.OOBTree import OOBTree

from horae.core.interfaces import IIntIdManager
from horae.lifecycle import lifecycle
from horae.cache import request

from horae.properties import interfaces


class PropertyChange(grok.Model, lifecycle.LifecycleAwareMixin):
    """ A change of multiple properties
    """
    grok.implements(interfaces.IPropertyChange)
    id = schema.fieldproperty.FieldProperty(interfaces.IPropertyChange['id'])

    def __init__(self):
        super(PropertyChange, self).__init__()
        self._properties = OOBTree()

    def properties(self):
        """ Iterator over the changed properties (name, value)
        """
        properties = self._properties.items()
        hidden = []
        if not checkPermission('horae.ViewHiddenProperties', self):
            hidden = self._properties.get('hidden', [])
        if not 'ALL' in hidden:
            for id, value in properties:
                if not id in hidden:
                    yield id, value

    def get_property(self, id, default=None):
        """ Return the specific property value
        """
        hidden = self._properties.get('hidden', [])
        if ((id in hidden or 'ALL' in hidden) and
            not checkPermission('horae.ViewHiddenProperties', self)):
            return default
        return self._properties.get(id, default)

    def set_property(self, id, value):
        """ Sets a property
        """
        self._properties[id] = value


class PropertiedMixin(object):
    """ An object storing dynamic properties and providing a history over them
    """
    grok.implements(interfaces.IPropertied)

    def __init__(self):
        super(PropertiedMixin, self).__init__()
        self._current = None

    @property
    def _properties(self):
        if not hasattr(self, '_props'):
            self._props = OOBTree()
        return self._props

    def _changes(self):
        if not 'changes' in self:
            self['changes'] = grok.OrderedContainer()
        return self['changes']

    def properties(self):
        """ Iterator over the available properties (IProperty)
        """
        providers = reversed([provider for name, provider in component.getAdapters((self,), interfaces.IProperties) if not name == ''])
        seen = []
        for provider in providers:
            for property in provider.properties():
                if property.id in seen:
                    continue
                seen.append(property.id)
                yield property

    @request.cache()
    def find_property(self, id):
        """ Trys to find and return the property having the specified id
        """
        providers = reversed([provider for name, provider in component.getAdapters((self,), interfaces.IProperties) if not name == ''])
        for provider in providers:
            property = provider.get_property(id)
            if property is not None:
                return property
        return None

    def new_change(self):
        """ Starts a new property change and returns it
        """
        self._current = PropertyChange()
        self._current.id = component.getUtility(IIntIdManager).nextId('property_change')
        order = [str(self._current.id), ] + list(self._changes().keys())
        self._changes()[str(self._current.id)] = self._current
        self._changes().updateOrder(order)
        return self._current

    def get_property(self, id, default=None):
        """ Return the specific property value
        """
        value = None
        if id in self._properties:
            value = self._properties[id]
        else:
            for change in self._changes().values():
                value = change.get_property(id)
                if value is not None:
                    self._properties[id] = value
                    break
        if value is None:
            return default
        return value

    def set_property(self, id, value):
        """ Sets a property on the currently active property change
        """
        self._current.set_property(id, value)
        self._properties[id] = value

    def changelog(self):
        """ Iterator over the history of property changes
        """
        hidden = checkPermission('horae.ViewHiddenProperties', self)
        for change in self._changes().values():
            if not hidden and 'ALL' in change.get_property('hidden', []):
                continue
            yield change

    def current(self):
        """ Returns the current property change
        """
        return self._current

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        if name in self._properties:
            return self._properties[name]
        for property in self.properties():
            if property.remember and name in property.field_names():
                return self.get_property(name)
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None


class TicketPropertiedMixin(PropertiedMixin):
    """ Mix in class for ticket propertied
    """

    def properties(self):
        """ Iterator over the available properties (IProperty)
        """
        providers = reversed([provider for name, provider in component.getAdapters((self,), interfaces.IProperties) if not name == ''])
        _marker = object()
        milestone = self.get_property('milestone', _marker)
        if milestone is _marker:
            for provider in providers:
                property = provider.get_property('milestone')
                if property:
                    milestone = property.default
                    break
        if milestone is not None:
            providers = [interfaces.ITicketProperties(milestone), ] + [provider for provider in providers]
        seen = []
        for provider in providers:
            for property in provider.properties():
                if property.id in seen:
                    continue
                seen.append(property.id)
                yield property


class PropertiesProxy(grok.Adapter):
    """ Proxy around IPropertied
    """
    grok.context(interfaces.IPropertied)
    grok.implements(interfaces.IPropertiesProxy)

    def __init__(self, propertied):
        self._propertied = propertied

    def __getattribute__(self, name):
        """ Returns the current property value
        """
        return getattr(object.__getattribute__(self, '_propertied'), name)

    def __setattr__(self, name, value):
        """ Sets the value to the last property change
        """
        if name == '_propertied':
            object.__setattr__(self, name, value)
        else:
            object.__getattribute__(self, '_propertied').set_property(name, value)


@grok.adapter(PropertiesProxy)
@grok.implementer(interfaces.IPropertied)
def propertied_of_properties_proxy(proxy):
    """ Returns the propertied of a :py:class:`PropertiesProxy`
    """
    return object.__getattribute__(proxy, '_propertied')
