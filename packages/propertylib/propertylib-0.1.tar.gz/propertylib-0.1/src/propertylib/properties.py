'''
Python's properties are very useful constructs that allows one to define 
getter and setter methods, while retaining a attribute interface. ``propertylib`` 
offers an alternate and way to define properties using the ``class`` syntax 
and also provide few specialized properties implementations that simplify some 
common use-cases.

The problem
-----------

The standard way to define a property with setter and getter methods is 
cumbersome and clutters the class namespace

>>> class Cls(object):
...     def _answer_get(self):
...         try:
...             return self._answer
...         except AttributeError:
...             return 42
...
...     def _answer_set(self, value):
...         self._answer = value
...
...     answer = property(_answer_get, _answer_set)

``propertylib`` provides a more convenient method, exploiting Python's 
metaclass mechanism

>>> from propertylib import *
>>> class Cls2(object):
...     class answer(std_property):
...         def fget(self):
...             try:
...                 return self._answer
...             except AttributeError:
...                 return 42
...
...         def fset(self, value):
...             self._answer = value

The new notation has less boilerplate code and does not clutter the class 
namespace with the two (usually) unecessary methods ``_answer_get`` and 
``_answer_set``.

Both ways are equivalent, for getters

>>> x = Cls(); x.answer
42
>>> y = Cls2(); y.answer
42

and for setters

>>> x.answer = 21; x.answer
21
>>> y.answer = 21; y.answer
21

The ``std_property`` class also provides a way to define the deleter, by 
defining the ``fdel`` method analogously as before. 

Specialized properties
----------------------

We also provide specialized properties that simplify usage in some common use 
cases. See the documentation on `default_property`, `auto_property`, and 
`cache_property`.   

API Documentation
-----------------
'''
import functools

__all__ = ['std_property', 'default_property', 'auto_property', 'cache_property']

class std_property(property):
    '''
    Creates property objects with setters, getters and deleters using a class 
    notation.
    
    Examples
    --------
    
    >>> class Cls(object):
    ...     class answer(std_property):
    ...         def fget(self):
    ...             try:
    ...                 return self._answer
    ...             except AttributeError:
    ...                 return 42
    ...
    ...         def fset(self, value):
    ...             self._answer = value
    ... 
    >>> x = Cls(); x.answer
    42
    >>> x.answer = 12; x.answer
    12
    '''
    class __metaclass__(type):
        def __new__(cls, name, bases, namespace):
            try:
                fget = namespace.get('fget', None)
                fset = namespace.get('fset', None)
                fdel = namespace.get('fdel', None)
                return std_property(fget, fset, fdel)
            except NameError:
                return type.__new__(cls, name, bases, namespace)

class default_property(property):
    '''
    A property that returns a default value, until it is manually set by the 
    user.
    
    Parameters
    ----------
    value : object
        The default value.
        
    Examples
    --------

    >>> class Cls(object):
    ...     answer = default_property(42)
    >>> x = Cls(); x.answer
    42
    >>> x.answer = 21; x.answer
    21
    '''
    def __new__(cls, value):
        return property.__new__(cls, fget=None, fset=None, fdel=None)

    def __init__(self, value):
        name = self.attr_name = '_cache_%s' % id(self)

        def fget(other):
            try:
                return getattr(other, name)
            except AttributeError:
                return value

        def fset(other, value):
            setattr(other, name, value)

        super(default_property, self).__init__(fget, fset)

    def clear(self, obj):
        '''
        Clear property's value 
        '''
        delattr(obj, self.attr_name)

class auto_property(property):
    '''
    A property that computes its value from 'func()' until the attribute is 
    manually set by the user.
    
    Parameters
    ----------
    func : callable
        Getter function: obj.attr <==> fget(obj).
        
    Examples
    --------
    Defines a class with an auto_property
    
    >>> class Cls(object):
    ...     @auto_property
    ...     def answer(self):
    ...         return 42

    Instantiate the object. The ``answer`` attribute already has
    a default value computed by the corresponding `answer` function.
    
    >>> x = Cls(); x.answer
    42
    >>> x.answer = 12; x.answer
    12
    '''
    def __new__(cls, func=None):
        return property.__new__(cls, fget=None, fset=None, fdel=None)

    def __init__(self, fget=None):
        self.orig_fget = fget
        name = self.attr_name = '_cache_%s' % id(self)

        @functools.wraps(fget)
        def ffget(other):
            try:
                return getattr(other, name)
            except AttributeError:
                return fget(other)

        def ffset(other, value):
            setattr(other, name, value)

        super(auto_property, self).__init__(ffget, ffset)

    def clear(self, obj):
        '''
        Clear property's value 
        '''
        delattr(obj, self.attr_name)

    class cls(object):
        'A class notation to auto_property'
        class __metaclass__(type):
            def __new__(cls, name, bases, namespace):
                try:
                    fget = namespace.get('fget', None)
                    if 'fset' in namespace:
                        raise NameError('cannot define fset in auto_properties')
                    if 'fget' in namespace:
                        raise NameError('cannot define fget in auto_properties')
                    return auto_property(fget)
                except NameError:
                    return type.__new__(cls, name, bases, namespace)

class cache_property(property):
    '''
    A property that implements an automatic cache of its value. It is useful
    for immutable objects that perform expensive computations or to provide 
    default values for attributes that somehow depends on the state of 
    the object. The default constructor allows for a *getter* method which 
    computes the value in cache and a *setter* that allows the user to 
    override the cache value. 
    
    Parameters
    ----------
    fget : callable
        Getter function: obj.attr <==> fget(obj)
        
    Notes
    -----
    
    The user can change explicitly some value in the property's cache by 
    calling the ``Class.property.save()`` method. It can also clear the cache
    using ``Class.property.clear()``.
        
    Examples
    --------
    
    Consider the class with a cache_property
    
    >>> class Cls(object):
    ...     @cache_property
    ...     def answer(self):
    ...         print 'Deep thought is computing...'
    ...         return 42

    The ``answer`` method is only called once, and its value is stored. 
    
    >>> x = Cls(); x.answer
    Deep thought is computing...
    42
    >>> x.answer
    42
    
    This value can be overridden by assignment
    
    >>> x.answer = 21; x.answer
    21
    
    Cache can be erased by the reset method
    
    >>> Cls.answer.clear(x); x.answer
    Deep thought is computing...
    42
    '''

    def __new__(cls, fget):
        def fset(other, value):
            setattr(other, attrname, value)

        new = cls.rw(fget, fset)
        attrname = '_cache_%s' % id(new)

        return new

    def __init__(self, fget):
        # Init must be empty in order to avoid the automatic calling of its
        # method after __new__ 
        pass

    @classmethod
    def rw(cls, fget, fset=None, fdel=None):
        '''
        Cached property that allows one to override the setter and deleter 
        methods. 
         
        Parameters
        ----------
        fget : callable
            Getter function: obj.attr <==> fget(obj)
        fset : callable 
            Setter function: obj.attr = value <==> fset(obj, value)
        fdel : callable
            Delete function: del obj.attr <==> fdel(obj)
            
        Example
        -------
        
        Defines a class with a cache_property
        
        >>> class Cls(object):
        ...     @cache_property.rw
        ...     def answer(self):
        ...         print 'Deep thought is computing...'
        ...         return 42
    
        Since no setter were defined, the answer attribute is read-only
         
        >>> x = Cls(); x.answer
        Deep thought is computing...
        42
        >>> x.answer = 21
        Traceback (most recent call last):
        ...
        AttributeError: can't set attribute
        '''

        # Getter
        @functools.wraps(fget)
        def ffget(other):
            try:
                return getattr(other, attrname)
            except AttributeError:
                value = fget(other)
                setattr(other, attrname, value)
                return value
        ffget.original = fget

        # Configure object
        new_obj = property.__new__(cls, ffget, fset, fdel)
        property.__init__(new_obj, ffget, fset, fdel)

        # This value will be updated in other closure functions
        new_obj.attrname = attrname = '_cache_%s' % id(new_obj)
        return new_obj

    def clear(self, obj):
        '''Erase the cache value.'''

        delattr(obj, self.attrname)

    def save(self, obj, value):
        '''Save the given 'value' on obj's cache for the attribute.'''

        setattr(obj, self.attrname, value)

    class cls(object):
        'A class notation to cache_property'
        class __metaclass__(type):
            def __new__(cls, name, bases, namespace):
                try:
                    fget = namespace.get('fget', None)
                    fset = namespace.get('fset', None)
                    fdel = namespace.get('fdel', None)
                    if fset is None and fdel is None:
                        return cache_property(fget)
                    else:
                        return cache_property.rw(fget, fset, fdel)

                except NameError:
                    return type.__new__(cls, name, bases, namespace)



if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
