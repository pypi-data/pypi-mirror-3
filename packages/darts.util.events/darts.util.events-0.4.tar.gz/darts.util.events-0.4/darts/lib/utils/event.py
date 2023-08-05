# -*- coding: utf-8 -*-
#
#  Deterministic Arts Utilities
#  Copyright (c) 2010 Dirk Esser
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

"""Simple event publisher

This module provides class for simple event publishing. The basic concept
here is the `Publisher`, which represents a set of registered listeners.
Listeners may either be functions or methods on arbitrary objects. The 
module supports weak references (in either case) to listeners.

You may use this module in order to implement `C#` style event handling.
The facility provided here is intended primarily for use cases, where
there is a somewhat strong coupeling between the origin of an event and
handlers for it. It is less applicable for situations, where the coupeling
is only weak.

Example::

    >>> from darts.lib.event import Subscription, Publisher
    >>> class ActiveObject(object):
    ...
    ...     def __init__(self):
    ...         super(ActiveObject, self).__init__()
    ...         self.property_change = Publisher()
    ...         self._name = None
    ...
    ...     def _get_name(self):
    ...         return self._name
    ...
    ...     def _set_name(self, value):
    ...         self._name = name
    ...         self.property_change.publish(self, 'name')
    ...
    ...     name = property(_get_name, _set_name)
    ...
    >>> ob = ActiveObject()
    >>> ob
    <ActiveObject at ...>
    >>> def listener(sender, property):
    ...    print sender, "changed value of property", property
    >>> ob.subscribe(listener)
    <SFHandle ...>
    >>> ob.name = "foo"
    <ActiveObject at ...> changed value of property name
    >>> ob.name
    foo
"""

from __future__ import with_statement

from logging import getLogger
from sys import exc_info
from weakref import ref as WeakRef
from threading import RLock


__all__ = (
    'Subscription', 'Publisher', 'ReferenceRetention', 'WEAK',
    'STRONG', 'log_publication_error',
)

log = getLogger(__name__)


class Subscription(object):

    """Handle with a publisher

    Instances of this class represent subscriptions of listener
    to event publishers. The subscription object can be used to 
    cancel the subscription, if event notification is no longer
    required.

    Handle objects are immutable after construction, with the
    exception, that handles created using a weak reference retention
    policy may change at any time, losing their internal listener
    object.

    For the sake of client application code, which wants to log
    the actual culprit in case of exceptions caught during event
    dispatching, a subscription provides read-only access to their
    underlying listener object and the method to be called on it.
    Be warned, that the values contained in the properties `listener`
    and `method` may only be "approximations", i.e., they may
    be different from the values passed in the `Publisher.subscribe`
    call, which was used to create the subscription instance. That
    said, the values provided through `listener` and `method` should
    usually be close enough to the original values that a failing
    listener can be identified.

    This class is not intended for subclassing outside of this
    module.
    """

    __slots__ = ('__weakref__',)

    def cancel(self):

        """Cancels the subscription
        
        This method cancels the subscription. The listener will 
        no longer rceive event notifications. If, however, there 
        is currently a `publish` call in progress on the publisher, 
        this subscription was obtained from, it is undefined, whether 
        the listener will receive notifications for any such pending 
        call.
        
        This method returns true, if the listener was unsubscribed 
        due to the call to this method, and false, if it had already 
        been unsubscribed and thus, the call did nothing.
        """
        
        raise NotImplementedError

    listener = property(lambda self: self._Subscription__target(), doc="""Listener object

       This property contains the actual listener object registered
       at the time, this subscription was created. If the subscription
       was made with a retention policy of `WEAK`, the value of this
       property may be `None`, if the listener object has since been
       deleted by the garbage collector.

       Note, that the value of this property may be different from 
       the value passed to `Publisher.subscribe` under certain 
       circumstances.

       This property is provided primarily for ther sake of error
       handlers, which want to log the actual culprit in case of 
       exceptions caught during event dispatching.""")

    method = property(lambda self: self._Subscription__method(), doc="""Method on listener

       This property contains a string, which names the method on the
       subscription's listener object, which is called during event 
       dispatching. Note, that the value of this property may be
       different from the value passed to `Publisher.subscribe` under
       certain circumstances.

       This property is provided primarily for ther sake of error
       handlers, which want to log the actual culprit in case of 
       exceptions caught during event dispatching.""")

        


## XXX: The optimization made for strong method references, namely,
##      to grab a bound function object, and discard the original
##      listener otherwise, does not play nicely with the `listener`
##      and `method` properties of subscriptions. Maybe, this case
##      should be de-optimized for the sake of exception loggers?



class Handle(Subscription):

    __slots__ = ('_Handle__publisher',)

    def __new__(klass, publisher):
        self = object.__new__(klass)
        self.__publisher = publisher
        return self

    def cancel(self):
        return self.__publisher._Publisher__forget(self)

    def __is_alive(self):

        """(internal)

        Called by a publisher in order to test, whether this subscription is still
        alive and should receive notifications. The implementatin must be provided 
        by subclasses. This implementation raises an exception.
        """

        raise NotImplementedError

    def __invoke(self, args, keys):

        """(internal)

        Called by a publisher in order to invoke the actual listener. The given `args`
        and `keys` are the positional arguments sequence/keyword argument dictionary
        to pass along. If the listener has been invalidated by garbage collection,
        the call must be ignored. The implementation must be provided by subclasses. 
        This implementation raises an exception.
        """

        raise NotImplementedError

    
class SFHandle(Handle):

    """(internal)

    This kind of subscription is used for strong references to functions (or
    targets, whose `__call__` method should be called.)
    """

    __slots__ = (
        '_SFHandle__function',
    )

    def __new__(klass, publisher, function):
        self = Handle.__new__(klass, publisher)
        self.__function = function
        return self

    def _Handle__is_alive(self):
        return True

    def _Handle__invoke(self, args, keys):
        self.__function(*args, **keys)
        return True

    def _Subscription__target(self):
        return self.__function

    def _Subscription__method(self):
        return '__call__'

    def __str__(self):
        return "<SFHandle %r at 0x%x>" % (self.__function, id(self),)

    __repr__ = __str__


class WFHandle(Handle):

    """(internal)

    This kind of subscription is used for weak references to functions (or
    targets, whose `__call__` method should be called.)
    """

    __slots__ = (
        '_WFHandle__function',
    )

    def __new__(klass, publisher, function):
        self = Handle.__new__(klass, publisher)
        self.__function = WeakRef(function)
        return self

    def _Handle__is_alive(self):
        return self.__function() is not None

    def _Handle__invoke(self, args, keys):
        function = self.__function()
        if function is None: return False
        else:
            function(*args, **keys)
            return True

    def _Subscription__target(self):
        return self.__function()

    def _Subscription__method(self):
        return '__call__'

    def __str__(self):
        function = self.__function()
        if function is None: return "<WFHandle (dead) at 0x%x>" % (id(self),)
        return "<SFHandle %r at 0x%x>" % (self.__function, id(self),)

    __repr__ = __str__



class WMHandle(Handle):

    """(internal)

    This kind of subscription is used for weak references to objects, when
    the method to call is not `__call__`.
    """

    __slots__ = (
        '_WMHandle__target',
        '_WMHandle__method',
    )

    def __new__(klass, publisher, target, method):
        self = Handle.__new__(klass, publisher)
        self.__target = WeakRef(target)
        self.__method = method
        return self

    def _Handle__is_alive(self):
        return self.__target() is not None

    def _Handle__invoke(self, args, keys):
        target = self.__target()
        if target is None: return False
        else:
            getattr(target, self.__method)(*args, **keys)
            return True

    def _Subscription__target(self):
        return self.__target()

    def _Subscription__method(self):
        return self.__method

    def __str__(self):
        target = self.__target()
        if target is None:
            return "<WMHandle (dead).%s at 0x%x>" % (self.__method, id(self),)
        return "<WMHandle %r.%s at 0x%x>" % (target, self.__method, id(self),)

    __repr__ = __str__


class ReferenceRetention(object):

    """Reference Retention Policy
    
    This enumeration describes, how a publisher should remember a given
    listener. The publisher may either use a plain, strong reference,
    which ensures, that the listener is kept as long as the publisher is
    alive or the subscription is cancelled, or a weak reference, which
    will automatically remove the listener, if the publisher is the only
    place in the process, which has references to it.
    """

    @staticmethod
    def STRONG(publisher, target, method):

        """Strong reference

        Use this value as reference retention policy in order to force
        a publisher to keep a strong reference to your listener around.
        This is actually the default value.
        """
        if method == '__call__': return SFHandle(publisher, target)
        return SFHandle(publisher, getattr(target, method))

    @staticmethod
    def WEAK(publisher, target, method):

        """Weak reference

        Use this value as reference retention policy in order to force
        a publisher to remember your listener using a weak reference.
        This allows Python's garbage collector to delete the listener
        even while it is still subscribed to a publisher.
        """
        if method == '__call__': return WFHandle(publisher, target)
        return WMHandle(publisher, target, method)


WEAK = ReferenceRetention.WEAK
STRONG = ReferenceRetention.STRONG

def reraise(exception, value, traceback, subscription, args, keys):

    """
    """

    raise exception, value, traceback


class Publisher(object):

    """Event publisher
    
    Instances of this class allow the dispatching of event notifications
    to interested parties. In order to receive notifications, listeners
    must be subscribed to the publisher. 

    This class is not intended to be subclassed.
    """

    __slots__ = (
        '__weakref__',
        '_Publisher__subscriptions',
        '_Publisher__exception_handler',
        '_Publisher__lock',
    )

    def __init__(self, exception_handler=reraise):
        super(Publisher, self).__init__()
        self.__subscriptions = ()
        self.__exception_handler = exception_handler
        self.__lock = RLock()
        
    def subscribe(self, listener, method="__call__", reference_retention=STRONG):
        
        """Subscribe a listener
        
        This method adds `listener` as new listener to receive event
        notifications via this publisher. If `method` is `None`, the
        listener should be a callable object, i.e., it should provide
        an implementation for method `__call__`, otherwise `method` 
        should be the name of the method to call on `listener` whenever
        an event occurs.
        
        The `reference_retention` value determines, whether the publisher
        keeps a strong reference to the listener around. It may be one
        of the constant values `WEAK` or `STRONG` defined in this module.
        If `WEAK` the listener will only be kept using a weak reference,
        and if `STRONG`, the listener will be remembered using a full
        (strong) reference.
        
        This method returns a subscription object, which can be used
        to cancel the subscription made. 

        Subclassing. This method is not intended to be overridden by
        subclasses.
        """
        
        if listener is None:
            raise ValueError, "listener must not be None"
        if reference_retention not in (WEAK, STRONG):
            raise ValueError, "unsupported reference retention policy"
        if not isinstance(method, str):
            raise ValueError, "method must be a string"
        subscription = reference_retention(self, listener, method)
        with self.__lock:
            buffer = list()
            for element in self.__subscriptions:
                if element._Handle__is_alive():
                    buffer.append(element)
            buffer.append(subscription)
            self.__subscriptions = tuple(buffer)
        return subscription
            
    def __forget(self, subscription):

        """(internal)

        Removes the subscription passed in as `subscription`. This
        method also uses the chance to clean-up dead subscription which
        have been invalidated by garbage collection.
        """

        buffer = list()
        seen = False    
        with self.__lock:
            for element in self.__subscriptions:
                if element is subscription:
                    seen = True
                elif element._Handle__is_alive():
                    buffer.append(element)
            self.__subscriptions = tuple(buffer)
        return seen
    
    def publish(self, *args, **keys):
        
        """Publish an event
        
        This method notifies all subscribed listeners, that an event
        has occurred. The given arguments `args` and `keys` will be 
        passed down to each listener called.

        This method is essentially a convenience interface for
        method `publish_safely`, passing the publisher's own 
        exception handler function (the one specified at construction
        time).

        Subclassing. This method is not intended to be overridden by
        subclasses.
        """
        
        return self.publish_safely(self.__exception_handler, *args, **keys)

    def publish_safely(self, handler, *args, **keys):

        """Publish an event
        
        This method notifies all subscribed listeners, that an event
        has occurred. The given arguments `args` and `keys` will be 
        passed down to each listener called.

        If a listener raises an exception while being notified, this
        method calls the given error handler `handler`, which must be
        a function with the signature

           def error_handler(exception, value, traceback, subscription, args, keys):
              pass 

        The arguments will be supplied as follows:

           `exception` the exception caught
           `value` the associated exception value
           `traceback` the stack trace
           `subscription` subscription of the failed listener
           `args` event arguments as supplied to this method
           `keys` event arguments as supplied to this method

        The exception may perform any operations required to handle
        the exception, for example, simply log it, ignore it alltogether
        or re-raise it. The last option will abort the current 
        dispatch.

        Subclassing. This method is not intended to be overridden by
        subclasses.
        """

        # For CPython, just reading the field should be sufficient,
        # but I don't know about the others (in particular, Jython),
        # so let's prefer being safe over being sorry:
        
        with self.__lock:
            subscriptions = self.__subscriptions
        
        for subscription in subscriptions:
            try:
                subscription._Handle__invoke(args, keys)
            except:
                exception, value, traceback = exc_info()
                handler(exception, value, traceback, subscription, args, keys)


def log_publication_error(exception, value, traceback, subscription, args, keys):

    """Publisher exception handler

    This function can be used as exception handler at publisher
    construction time or as handler argument to `publish_safely`.
    It will log any exceptions using the Python `logging` module,
    with a log level of error. This function allows other listeners
    to be notified by returning normally.
    """

    log.error(u"listener %r.%s raised exception during event notification with arguments %r",
              subscription.listener, 
              subscription.method,
              (args, keys),
              exc_info=(exception, value, traceback))

