# -*- coding: utf-8 -*-

from darts.lib.utils.event import Publisher, ReferenceRetention as RR


class PublisherAttribute(object):

    """Event publisher attribute

    Instances of this class act as property descriptors, which
    manage event publishers. The first time, the attribute is 
    referenced on a given instance, a new publisher instance is
    created.
    """

    __slots__ = (
        '__weakref__', 
        '_PublisherAttribute__key',
        '_PublisherAttribute__factory',
        '_PublisherAttribute__doc',
    )

    def __new__(klass, key, factory=lambda ob: Publisher(), doc=None):
        self = object.__new__(klass)
        self.__key = key
        self.__factory = factory
        self.__doc = doc
        return self

    key = property(lambda self: self.__key)
    factory = property(lambda self: self.__factory)
    doc = property(lambda self: self.__doc)

    def __get__(self, instance, klass):
        if instance is None:
            return self
        else:
            key = self.__key
            publisher = getattr(instance, key, None)
            if publisher is None:
                publisher = self.__factory(instance)
                setattr(instance, key, publisher)
            return publisher
        
    def new_attribute(self, key, name=None, doc=None):

        """Create a new published attribute

        This method returns a new PublishedAttribute descriptor, which
        uses the event publisher managed by this publisher attribute
        to notify subscribed listeners about changes made to the attribute
        value.
        """

        return PublishedAttribute(self, key, name=name, doc=doc)

    def publish_for(self, instance, *event_args, **event_keys):

        """Publish an event

        This method publishes the event represented by `event_args` and
        `event_keys` on the managed publisher of `instance`. If the
        publisher has not yet been created (which implies, that there is
        nobody listening on events), this method does nothing.
        """

        key = self.__key
        publisher = getattr(instance, key, None)
        if publisher is not None:
            publisher.publish(*event_args, **event_keys)


class PublishedAttribute(object):

    __slots__ = (
        '__weakref__',
        '_PublishedAttribute__key',
        '_PublishedAttribute__name',
        '_PublishedAttribute__publisher',
        '_PublishedAttribute__doc',
    )

    def __new__(klass, publisher, key, name=None, doc=None):
        self = object.__new__(klass)
        self.__key = key
        self.__name = name or key
        self.__publisher = publisher
        self.__doc = doc
        return self

    key = property(lambda self: self.__key)
    name = property(lambda self: self.__name)
    doc = property(lambda self: self.__doc)

    def __get__(self, instance, klass):
        if instance is None: 
            return self
        else:
            try:
                return instance.__dict__[self.__key]
            except KeyError:
                raise AttributeError

    def __set__(self, instance, value):
        key, name, publisher = self.__key, self.__name, self.__publisher
        marker = object()
        old_value = instance.__dict__.get(key, marker)
        if old_value is marker:
            instance.__dict__[key] = value
            publisher.publish_for(instance, instance, name, None, value, 'after')
        else:
            if old_value != value:
                publisher.publish_for(instance, instance, name, old_value, value, 'before')
                instance.__dict__[key] = value
                publisher.publish_for(instance, instance, name, old_value, value, 'after')
    
    def __delete__(self, instance):
        if self.__key in instance.__dict__:
            del instance.__dict__[self.__key]




class VerboseObject(object):

    """Example object

    This class is a basic example using the property-notification
    machinery defined above. It features three attributes, two of
    which will send notifications whenever their value changes.
    """

    __slots__ = (
        '__weakref__', 
        '__dict__',
        '__on_attribute_change__',
    )

    on_attribute_change = PublisherAttribute('__on_attribute_change__', doc="""This object's attribute-change event publisher

        This property contains an event publisher, to which you may subscribe
        listeners in order to receive notifications about changes made to
        attributes of a particular instance.""")

    id = on_attribute_change.new_attribute('id', doc="""This object's identifier
       
        This attribute contains the object primary identifier (an integer
        number). Note, that the identifier is initially None for new objects,
        and will be set when the instance is saved for the first time.""")

    display_name = on_attribute_change.new_attribute('display_name', doc="""This object's display name

        The value of this property is a short unicode string, which should
        be used (in preference to other representations) to stand in for 
        this object when information about it has to be constructed intended
        for a human reader.""")
    
    def __init__(self, id=None, display_name=None):
        self.__dict__['id'] = id
        self.__dict__['display_name'] = display_name


def printer(*args, **keys):
    print args, keys

vb = VerboseObject()
vb.display_name = U"Init"
vb.on_attribute_change.subscribe(printer)
vb.display_name = U"Foo"
vb.display_name = U"Bar"
