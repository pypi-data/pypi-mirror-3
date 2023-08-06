import os
import contextlib
import functools
import anydbm
import cPickle as pickle

class pproperty(property):
    OPEN_DATABASES = {}
    def __new__(cls, arg0, *args, **kwds):
        if isinstance(arg0, basestring):
            def decorator(func):
                return pproperty(func, attr_name=arg0, *args, **kwds)
            return decorator
        else:
            return super(pproperty, cls).__new__(cls, fget=None, fset=None, fdel=None)

    def __init__(self, fget, attr_name=None, attr_type=object, cls=None,
                 db_key=None, db_path=None, db_sync=True, obj_key=None):
        '''
        Property that implements an automatic cache of its value with 
        persistence across sections. It is useful to store the results of 
        expensive computations for later use.
        
        Arguments
        ---------
        
        fget : callable
            Getter function: obj.attr <==> fget(obj)

        attr_name : string
            Name of attribute corresponding to the given property. Automatically
            configured by calling pproperty(cls).
            
        attr_type : None
            Optional type for the attribute object. This is used to build 
            custom serializers or to use non-picklable data.
            
        cls : None
            Class that the attribute belongs to. The class is usually not 
            ready when pproperty() is called. However, this attribute is 
            automatically configured by calling pproperty(cls).
            
        db_key : string
            Name key used to access the attributte's value on the DB.
            
        obj_key : callable (obj) -> string
            The result of obj_key(obj) identifies obj and is appended to 
            'db_key' before hitting the DB. This is necessary to enable that 
            different objects of the same class can have different values of
            their persistent properties.
            
        db_path : string
            Path to database file.
            
        db_sync : bool
            If True, the DB is sync'ed at every write access. This behavior
            incurs in a (possibly substantial) performance penalty, but is
            safer to avoid data-loss.
            
        Example
        -------
        
        # Defines a class with a cache-able property
        >>> @pproperty.cls
        ... class Foo(object):
        ...     @pproperty
        ...     def answer(self):
        ...         print 'Deep thought is computing...'
        ...         return 42
    
        # Instantiate the object
        >>> bar = Foo()
        >>> del bar.answer
        >>> bar.answer
        Deep thought is computing...
        42
        >>> bar.answer
        42
        '''

        self.attr_name = attr_name
        self.attr_type = attr_type
        self.obj_key = obj_key
        self.orig_fget = fget
        self.db_sync = db_sync
        self.db_key = db_key
        self.cls = cls
        self.db_path = os.path.path(db_path or 'cached.db')

        def ffget(obj):
            try:
                return getattr(obj, self.cache)
            except AttributeError:
                with self.db() as db:
                    key = self.get_key(obj)
                    try:
                        value = self.db_decode(db[key])
                    except KeyError:
                        value = fget(obj)
                        db[key] = self.db_encode(value)
                        db.num_writes += 1
                        if self.db_sync:
                            db.sync()
                    setattr(obj, self.cache, value)
                    return value

        def ffdel(obj):
            cache = self.cache
            if hasattr(obj, cache):
                delattr(obj, cache)
            with self.db() as db:
                del db[self.get_key(obj)]

        super(pproperty, self).__init__(ffget, None, ffdel)

    def get_key(self, obj):
        '''Return key that represents a given obj/attribute in the DB.'''

        key = self.db_key
        if self.obj_key is not None:
            key = '%s.%s' % (key, self.obj_key(obj))
        elif hasattr(obj, 'db_key'):
            key = '%s.%s' % (key, obj.db_key)
        return key

    @contextlib.contextmanager
    def db(self):
        # Get database --- context.__enter__()
        try:
            db = self.OPEN_DATABASES[self.db_path]
        except KeyError:
            db = self.OPEN_DATABASES[self.db_path] = anydbm.open(self.db_path, 'c')
            db.num_writes = 0
        yield db

        # Clean database --- context.__exit__()
        if self.db_sync or db.num_writes % 20 == 0:
            db.sync()

    def db_encode(self, obj):
        '''Return string representation of obj. By default, it uses pickle to 
        construct this string.'''

        return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)

    def db_decode(self, st):
        '''Build object from its string representation.'''

        return pickle.loads(st)

    @property
    def cache(self):
        return '_' + self.attr_name

    @staticmethod
    def cls(cls=None, **kwds):
        # kwds decorate method. Must return a decorator that will be 
        # applied to a type.
        if cls is None:
            def decorator(cls):
                return pproperty.cls(cls, **kwds)
            return decorator

        # Decorate class with property attrs
        for attr_name in dir(cls):
            prop = getattr(cls, attr_name)
            if isinstance(prop, pproperty):
                if prop.cls is None:
                    prop.cls = kwds.pop('cls', cls)
                if prop.attr_name is None:
                    prop.attr_name = kwds.pop('attr_name', attr_name)
                if prop.db_key is None:
                    default_key = '%s.%s.%s' % (cls.__module__, cls.__name__,
                                                attr_name)
                    prop.db_key = kwds.pop('db_key', default_key)

                # Set keyword attributes 
                for k, v in kwds.items():
                    setattr(prop, k, v)

                # Ensure that db_path is an absolute path
                prop.db_path = os.path.path(prop.db_path)
        return cls

    @staticmethod
    def close_all():
        for k, db in pproperty.OPEN_DATABASES.items():
            db.close()
            del pproperty.OPEN_DATABASES[k]

    @staticmethod
    def sync_all():
        for k, db in pproperty.OPEN_DATABASES.items():
            db.sync()

pproperty.off = property
pproperty.on = pproperty

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
