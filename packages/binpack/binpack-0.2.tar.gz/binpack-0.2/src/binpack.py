'''
**Binpack** implements a protocol for binary packing of data. Binpack classes 
can be used to easily create user defined file types.

Files packed using the ``binpack`` protocol will have a small *header* section 
that holds the file type and version information. The ``body`` part is a 
sequence of named data streams. These data streams can be converted 
transparently into/from Python objects and are accessed using a dictionary 
interface. The keys in this dictionary are sorted in a predictable order.

Usage
-----

The easiest way to create new packing type is to use the ``new_type()`` class 
method of `BinPack`.   

>>> myfile = BinPack.new_type('myfile', header='myfile', version='0.1')

Any number of fields of different types can be added

>>> myfile.add_field('foo')
>>> myfile.add_field('bar', Compressed(Bytes('bar has a default value!')))

The order in which these fields are created is important because it is the same
order that data is stored in the file. It is a good practice to leave the fields
that hold large amounts of data to the end. Otherwise, these large chunks of 
data will be scanned in order to access a few bytes from a field that was saved 
in the end of the data stream.

After all fields are configured, the new class must be locked. It is not 
possible to add new fields to locked classes. But once the class is locked, it 
is ready to create instances. Locked classes cannot be unlocked and should not 
be modified in any way.

>>> myfile.lock()

A ``BinPack`` object opened in 'writing' mode works like a dictionary. When you 
assign some value to a key, it is automatically serialized and saved to the
file.

>>> F = StringIO()
>>> with myfile(F, mode='w') as data:
...     data['foo'] = 'data for foo'
...     F.getvalue()             # data is written to F as soon as possible
'\\xffmyfile\\xff0.1\\xff\\x0cdata for foo'

When the file is closed (which is automatic using the ``with`` statement, 
but manual otherwise), it writes any unwritten data to the file. If a field 
that does not have a default values was not assigned by the user, a ValueError 
is raised.

The data for the 'bar' field were automatically compressed in the data stream. 
Its default value should read 'bar has a default value!'. Instead we
see a bunch of seemly random bytes

>>> F.getvalue()
'\\xffmyfile\\xff0.1\\xff\\x0cdata for foo x\\x9cKJ,R\\xc8H,VHTHIMK,\\xcd)Q(K\\xcc)MU\\x04\\x00h\\xf1\\x08v'

Reading is similar to writing, and data is automatically converted to its
desired type
  
>>> F2 = StringIO(F.getvalue())
>>> with myfile(F2, close=True) as data:
...     data['foo'], data['bar']
('data for foo', 'bar has a default value!')

The ``close=True`` parameter used above tells the `BinPack` instance to 
automatically close the input file. This avoids a nested with statement that
would be necessary for a safe manipulation of files.

>>> F2.closed, F.closed
(True, False)

Converters
----------

(Not ready yet)

Versioning
----------

(Not ready yet)

Data format
-----------

`binpack` uses a method for storing data that can be portable across different
languages. Of course, if portability is an issue, python-specific fields such 
as 'Pickle' must be avoided. 

Data is stored by `binpack` as a predictable sequence of bytes. 

The *header* part: 

  - The first byte of the file is always 0xFF. 
  - The following bytes are the ascii characters in the user-defined header, 
    which are specific of each `BinPack` subclass. 
  - Another 0xFF  marks the end of the header. 
  - The version string is appended and it is followed by a third 0xFF byte, 
    which sinalizes the end of the header.
    
The *body* part:

  Each field is associated in the file with a sequence of bytes. Before this
  sequence starts, however, we must tell how many bytes are present. This is 
  done using the following protocol:
  
  - The first byte is read. If it is less than 2^7, it is interpreted as the
    size of the byte stream. This number of bytes is read and assigned to the 
    field.
  - If the byte is greater than or equal to 2^7, the bytes are read until a byte
    smaller than 2^7 is found. The numbers greater than or equal 2^7 are 
    subtracted by 2^7. The sequence of numbers is then interpreted as a single
    number formed by a sequence of 7-bit integer in little-endian order. 
    
    That is, if the bytes are b1, b2, ..., bn the result is given by 
       
       N = (b1-128) + 2^7 * (b2-128) + 2^14 * (b3-128) + ... + 2^(n-1) * bn.
    
    The last byte was not subtracted by 128 (2^7) because it was already smaller
    than 128. N is then the size of the following byte stream. This 
    number of bytes is then read and assigned to the current field.
        
The *header* and *body* nomenclature used in ``binpack`` refers only to how
data is packed as binary stream. Of course, user formats may consider many 
fields in the *body* (in the sense of binpack) to be part of the header
of its file and only a few fields that hold the bulk of the data to be part of
the file body.

API Documentation
-----------------

Class methods in BinPack
````````````````````````

.. autoclass:: BinPack
   :members: set_header, get_header, set_version, get_version, add_field, 
             insert_field, del_field, lock, is_ready, new_type
             
Instance methods in BinPack
```````````````````````````

.. autoclass:: BinPack
   :members: close


Field types
```````````

.. autoclass:: Field
   :members: encoder, decoder, default, default_enc
   
.. autoclass:: Bytes
   
.. autoclass:: Pickle
   
.. autoclass:: Compressed

Utility functions
`````````````````

.. autofunc:: raw_unpack

.. autofunc:: header

.. autofunc:: version

.. autofunc:: full_header
'''
__all__ = ['BinPack', 'Field', 'Bytes', 'Pickle', 'Compressed',
           'raw_unpack', 'header', 'version', 'full_header']

import collections
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class voiddict(collections.MutableMapping):
    def __delitem__(self, key):
        raise KeyError(key)
    __getitem__ = __setitem__ = __delitem__

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

BinPack = None
class BinPack(collections.Mapping):
    '''Packs binary data in a file.
    
    Parameters
    ----------
    F : file object
        File to be  read or written.
    mode : 'r' or 'w'
        Initialize binary pack in (r)ead or (w)rite mode.
    close : bool
        If True, it will also closes F when the ``.close()`` method is 
        invoked.
    atomic : bool
        In normal operation, it tries to save data as soon as possible and tries
        to delay reading for as long as possible. If ``atomic`` is True, 
        these operations are all performed at once.
    keep_items : True
        It keeps a copy of objects inserted or written to file. For large
        files, it may be a good idea to delete these objects once they are 
        not needed anymore. If ``keep_items`` is False, it tries to delete 
        objects ASAP. This means that most of the keys can be accessed
        (read or write) only once.
    '''

    class __metaclass__(type(collections.Mapping)):
        def __new__(cls, name, bases, namespace):

            # Initializes the BinPack class
            if BinPack is None:
                return type(collections.Mapping).__new__(cls, name, bases, namespace)

            # Initializes a BinPack sub-class
            else:
                # Check bases
                if len(bases) > 1:
                    raise TypeError('BinPack subclasses do not accept multiple inheritance')

                # Ensure the locking mechanism
                base = bases[0]
                if not base.is_locked():
                    raise TypeError('Cannot subclass unlocked classes')

                # Creates new type and update its class dictionary
                new = type(collections.Mapping).__new__(cls, name, bases, namespace)
                if base is not BinPack:
                    new._cls_dict_ = {'fields': base._cls_dict_['fields'].copy()}
                else:
                    new._cls_dict_ = {}
                return new

    _cls_dict_ = {}

    def __new__(cls, *args, **kwds):
        if cls.is_locked():
            return object.__new__(cls)
        else:
            tname = cls.__name__
            msg = 'Class "%s" must be locked before instantiating objects' % tname
            raise TypeError(msg)

    def __init__(self, F, mode='r', close=False, atomic=False, keep_items=True):
        self._processed = set()
        self._raw = {}
        self._items = {} if keep_items else voiddict()
        self._ok = []
        self._sep = '\xff' if self.get_header()[0] == '\xff' else '\n'
        self._fields = self._cls_dict['fields']
        self._close = close
        self.closed = False

        # Checks if mode is compatible with file's mode
        if mode in ('r', 'w'):
            self.mode = mode
        else:
            raise ValueError("mode must be either 'r' or 'w', got: '%s'" % mode)
        if mode not in getattr(F, 'mode', 'rw'):
            raise ValueError("mode '%s' is incompatible with F's mode, '%s'" % (mode, F.mode))

        # Chooses file to save using atomic/non-atomic mode
        if atomic:
            self._file_after = F
            if self.mode == 'r':
                self.file = StringIO(F.read())
            else:
                self.file = StringIO()
        else:
            self._file_after = None
            self.file = F

        # Reads/writes the header/version to file
        if self.mode == 'r':
            self._data = raw_unpack(self.file)
            header = next(self._data)
            version = next(self._data)

            if header != self.get_header():
                raise ValueError("bad header: %s" % repr(header))
            if version != self.get_version():
                raise ValueError("bad version: %s" % repr(version))

            self._fields_it = iter(self._fields)
            self._data = ((next(self._fields_it), data) for data in self._data)
        else:
            self.file.write(self._cls_dict['full_header'])

    #===========================================================================
    # Context Manager/File
    #===========================================================================
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except ValueError:
            if exc_val is None:
                raise
        return False

    def close(self):
        '''Close file.'''

        try:
            if self.mode == 'w':
                keys = set(self) - self._processed
                fields = self._fields
                for key in keys:
                    default = fields[key].default()
                    if default is not None:
                        self[key] = default
                    else:
                        raise ValueError("missing data for field '%s'" % key)

                if self._file_after is not None:
                    data = self.file.getvalue()
                    self.file = self._file_after
                    self.file.write(data)
        finally:
            if self._close:
                self.file.close()

    def _assure_opened(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')

    def _write(self, data):
        self._assure_opened()
        self.file.write(bytes7num(len(data)))
        self.file.write(data)

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def _cls_dict(self):
        return type(self)._cls_dict_

    #===========================================================================
    # Abstract methods
    #===========================================================================
    def __getitem__(self, key):
        self._assure_opened()
        if key not in self._fields:
            raise KeyError('invalid key: %s' % key)
        elif key in self._items:
            return self._items[key]
        elif key in self._processed:
            raise KeyError("already retrieved: %s" % key)

        # In read mode, it tries to fetch from the file
        if self.mode == 'r':
            # Check if data is in raw
            try:
                data = self._raw.pop(key)
            except KeyError:
                pass
            else:
                decoder = self._fields[key].decoder
                value = decoder(data)
                self._processed.add(key)
                self._items[key] = value
                return value

            # Tries to fetch data from file
            for k, data in self._data:
                self._raw[k] = data
                if k == key:
                    return self[key]

            raise RuntimeError('should never reach here\n\tkey: %s\n\tdata: %s' % (key, self._raw.keys()))

        # In write mode, it checks for default values
        else:
            try:
                return self._raw[key]
            except KeyError:
                default = self._fields[key].default()
                if default is not None:
                    return default
                else:
                    raise KeyError(key)

    def __iter__(self):
        return iter(self._fields)

    def __len__(self):
        return len(self._fields)

    #===========================================================================
    # Magic methods
    #===========================================================================
    def __setitem__(self, key, value):
        self._assure_opened()
        if self.mode == 'r':
            raise ValueError('cannot set items in read mode')

        if key in self._processed:
            raise ValueError('key already saved to file')
        self._items[key] = self._raw[key] = value
        keys = list(self)
        for k in keys[len(self._ok):]:
            try:
                value = self._raw.pop(k)
            except KeyError:
                break
            else:
                encoder = self._fields[k].encoder
                data = encoder(value)
                self._write(data)
                self._ok.append(k)
                self._processed.add(k)

    #===========================================================================
    # Subtypes creation
    #===========================================================================
    @classmethod
    def new_type(cls, name, header=None, version=None, binary=True):
        '''Returns a new BinPack sub-type'''

        class NewType(cls):
            pass
        NewType.__name__ = name

        if header is not None:
            NewType.set_header(header)
        if version is not None:
            NewType.set_version(version)
        return NewType

#TODO: implement versioning
#    @classmethod
#    def new_version(cls, version=None):
#        cls._assure_locked()
#        raise NotImplementedError

    #===========================================================================
    # Locking mechanism
    #===========================================================================
    @classmethod
    def is_locked(cls):
        '''Return True when class is ready to instantiate methods'''

        return cls._cls_dict_.get('locked', False)

    @classmethod
    def lock(cls):
        '''Prevents class from changing and allows creation of instances'''

        dic = cls._cls_dict_

        # Check if class has the header and version are set properly
        if 'header' not in dic:
            raise ValueError("must set 'header' first")
        if 'version' not in dic:
            raise ValueError("must set 'version' first")


        # Check if the class has some registered field 
        if not dic.get('fields', None):
            raise ValueError('class must have at least one registered field')

        # Raw header, version and full header
        binary = dic['binary']
        dic['sep'] = ('\xff' if binary else '\n')
        header = dic['header']
        version = dic['version']
        dic['raw_header'] = ('\xff%s\xff' if binary else '%s\n') % header
        dic['raw_version'] = ('%s\xff' if binary else '%s\n') % version
        dic['full_header'] = ('\xff%s\xff%s\xff' if binary else '%s\n%s\n') % (header, version)

        # Lock it
        dic['locked'] = True

    @classmethod
    def _assure_unlocked(cls):
        if cls._cls_dict_.get('locked', False):
            raise RuntimeError('class must be unlocked in order to accept changes')

    @classmethod
    def _assure_locked(cls):
        if not cls._cls_dict_.get('locked', False):
            raise RuntimeError('class must be locked in order to perform this operation')

    #===========================================================================
    # Registering functions
    #===========================================================================
    @classmethod
    def set_header(cls, header):
        '''Defines an ascii string that serves as the file header.'''
        #TODO: implement ascii data streams with base64 encoding

        cls._assure_unlocked()
        header = unicode(header, 'ascii').encode('ascii')
        cls._cls_dict_['header'] = header
        cls._cls_dict_['binary'] = True

    @classmethod
    def set_version(cls, version):
        '''Register an ascii string to represent the file version.
         
        Versioning may be needed if the data format changes with time.'''

        cls._assure_unlocked()
        version = unicode(version, 'ascii').encode('ascii')
        cls._cls_dict_['version'] = version

    @classmethod
    def add_field(cls, field, converter=None, force=False):
        '''Register a field associating a data type and a default value.'''

        cls._assure_unlocked()
        fields = cls._cls_dict_.setdefault('fields', collections.OrderedDict())
        if field in fields and not force:
            raise ValueError("field '%s' already exists!" % field)

        # Update list and dictionaries
        if isinstance(converter, type) and issubclass(converter, Field):
            converter = converter()
        elif converter is None:
            converter = Bytes()

        if isinstance(converter, Field):
            fields[field] = converter
        else:
            raise TypeError('invalid converter of type %s' % type(converter))

    @classmethod
    def del_field(cls, field):
        '''Register a field associating a data type and a default value.'''

        cls._assure_unlocked()
        fields = cls._cls_dict_.setdefault('fields', collections.OrderedDict())
        del fields[field]

    @classmethod
    def insert_field(cls, field, key, converter=None):
        '''Register a field before the given key or index.'''

        cls._assure_unlocked()
        fields = cls._cls_dict_.setdefault('fields', collections.OrderedDict())
        if field in fields:
            raise ValueError("field '%s' already exists" % field)

        items = fields.items()
        idx = key if isinstance(key, int) else list(fields).index(key)
        head, tail = items[:idx], items[idx:]

        fields = collections.OrderedDict(head)
        cls._cls_dict_['fields'] = fields
        try:
            cls.add_field(field, converter)
        finally:
            fields.update(tail)

    #===========================================================================
    # Class getters
    #===========================================================================
    @classmethod
    def get_header(cls):
        return cls._cls_dict_['header']

    @classmethod
    def get_version(cls):
        return cls._cls_dict_['version']

    @classmethod
    def get_fields(cls):
        return cls._cls_dict_['fields'].copy()

#===============================================================================
# Converter fields
#===============================================================================
class Field(object):
    '''Base class for all field types'''

    def __init__(self, default=None):
        ''' Field(default) => creates a field with an optional value'''
        self._default = default

    def encoder(self, obj):
        '''Convert arbitrary object to bytes data.
        
        *Must be overridden in child classes*'''

        raise NotImplementedError('must be implemented in child classes')

    def decoder(self, data):
        '''Convert a data stream back to object.
        
        *Must be overridden in child classes*'''

        raise NotImplementedError('must be implemented in child classes')

    def default(self):
        '''Return the default value for the field'''
        return self._default

    def default_enc(self):
        '''Return a string with the serialized default value for the field'''
        return self.encoder(self.default())

class Bytes(Field):
    '''Class for byte string data. 
    
    This is the default data type for any field'''

    def encoder(self, obj):
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, basestring):
            return str(obj)
        else:
            raise TypeError('expected string, got %s' % type(obj))

    def decoder(self, data):
        return data

class Serializer(Field):
    def serializers(self):
        '''It must return a tuple of (encoder, decoder) functions. The arguments
        from the init method are passed to this function by default. 
        
        e.g., the Pickle serializer return the pickle.dumps, and pickle.loads 
        functions.
        '''
        raise NotImplementedError('must be implemented in child classes')

    def __init__(self, default=None, *args, **kwds):
        super(Serializer, self).__init__(default)
        self._encoder, self._decoder = self.serializers(*args, **kwds)

    def encoder(self, obj):
        try:
            return self._encoder(obj)
        except:
            print obj
            raise

    def decoder(self, data):
        try:
            return self._decoder(data)
        except:
            print repr(data)
            raise

class Pickle(Serializer):
    '''Serialize python objects using the pickle protocol
    
    Examples
    --------
    
    >>> pickle_file = BinPack.new_type('json_file', 'JSON', '0.1')
    >>> pickle_file.add_field('data', Pickle())
    >>> pickle_file.lock()
    >>> F = StringIO()
    >>> with pickle_file(F, 'w') as data:
    ...     data['data'] = [None, 1, 'two']
    >>> F.seek(0)
    >>> with pickle_file(F) as data:
    ...     print(data['data'])
    [None, 1, 'two']
    '''

    def serializers(self, protocol):
        '''Loads pickle module'''

        try:
            import cPickle as pickle
        except ImportError:
            import pickle
        import functools

        dumps = functools.partial(pickle.dumps, protocol=protocol)
        return (dumps, pickle.loads)

    def __init__(self, default=None, protocol=2):
        super(Pickle, self).__init__(default, protocol)

class JSON(Serializer):
    '''Serialize a JSON structure.
    
    Examples
    --------
    
    >>> json_file = BinPack.new_type('json_file', 'JSON', '0.1')
    >>> json_file.add_field('data', JSON())
    >>> json_file.lock()
    >>> F = StringIO()
    >>> with json_file(F, 'w') as data:
    ...     data['data'] = {'foo': 'bar', 'spam': ['ham', 'eggs']}
    >>> F.getvalue()                                        # doctest: +ELLIPSIS
    '...{"foo": "bar", "spam": ["ham", "eggs"]}'
    '''

    def serializers(self):
        '''Loads dumps and loads functions from the simplejson or json modules'''

        try:
            import simplejson as json
        except ImportError:
            import json

        return (json.dumps, json.loads)

class Compressed(Serializer):
    '''Compressed can be applied to any field in order to compress an 
    arbitrary data stream. 
    
    Parameters
    ----------
    filter : Filter instance
        The original filter. Its data will be compressed in the file.
    method : str
        A string describing the compression method. Currently, only 'bz2' 
        and 'zlib' are supported
    '''
    def __init__(self, filter, method='zlib', **kwds): #@ReservedAssignment
        self.compress, self.decompress = self.method(method, **kwds)
        self.filter = filter

    def encoder(self, obj):
        data = self.filter.encoder(obj)
        return self.compress(data)

    def decoder(self, data):
        data = self.decompress(data)
        return self.filter.decoder(data)

    def default(self):
        return self.filter.default()

    def default_enc(self):
        data = self.filter.default_enc()
        return self.compress(data)

    #===========================================================================
    # Compressing methods
    #===========================================================================
    @classmethod
    def method(cls, method, **kwds):
        if method == 'bz2':
            import bz2
            return bz2.compress, bz2.decompress
        elif method == 'zlib':
            import zlib
            return zlib.compress, zlib.decompress
        else:
            raise ValueError("compression method '%s' is not supported" % method)

#===============================================================================
# Locks BinPack class
#===============================================================================
BinPack.set_header(header='<binary>')
BinPack.set_version('0.1')
BinPack.add_field('data')
BinPack.lock()

#===============================================================================
# Utility functions
#===============================================================================
def bytes7num(n):
    '''Return number as a string of terms that can be read by read_num()'''
    data = []
    if n == 0:
        return chr(0)
    else:
        while n:
            n, mod = divmod(n, 128)
            data.append(mod)
        for idx in range(len(data) - 1):
            data[idx] = data[idx] + 128
        return ''.join(map(chr, data))

def read_num(F):
    '''Read the necessary number of bytes < 128 from F and construct a base-2^7
    number as output.'''
    nums = []
    n = 0
    while True:
        try:
            n = ord(F.read(1))
        except TypeError: # F.read(1) is empty
            if nums:
                raise ValueError('File ended before expected (%s bytes read)' % len(nums))
            else:
                return None

        if n > 127:
            nums.append(n - 128)
        else:
            nums.append(n)
            break
    return sum(n * (1 << (i * 7)) for (i, n) in enumerate(nums))

def raw_unpack(F, sep='\xff'):
    '''Iterates over all fields and returns raw data.
    
    The iterator that results from raw_upack(F) returns the header, version and
    each raw data field in the file object.  
    '''

    if sep == '\xff':
        byte = F.read(1)
        if byte != '\xff':
            raise ValueError('unexpected first byte: %s' % ord(byte))

    # Yield header
    c, chars = 1, []
    while c != sep and c:
        c = F.read(1)
        chars.append(c)
    chars.pop()
    yield ''.join(chars)

    # Yield version
    c, chars = 1, []
    while c != sep and c:
        c = F.read(1)
        chars.append(c)
    chars.pop()
    yield ''.join(chars)

    # Yield fields
    n = 0
    while n is not None:
        n = read_num(F)
        if n is not None:
            yield F.read(n)

    remaining = F.read()
    assert not remaining, 'some data was not read: %s' % remaining

def header(F):
    '''Returns the header of a file.'''

    try:
        pos = F.tell()
        header = next(raw_unpack(F))
    finally:
        F.seek(pos)
    return header

def version(F):
    '''Returns the version of a file.'''

    return full_header(F)[1]

def full_header(F):
    '''Returns a tuple with (header, version) for the file F.'''

    try:
        pos = F.tell()
        header = next(raw_unpack(F))
        version = next(raw_unpack(F))
    finally:
        F.seek(pos)
    return (header, version)

if __name__ == '__main__':
#    from StringIO import StringIO
#    F = StringIO()
#    with BinPack(F, mode='w') as data:
#        data['data'] = 'fdsdfsd sds'
#    print F.getvalue()
#
#    F2 = StringIO(F.getvalue())
#    print header(F2)
#    with BinPack(F2) as data:
#        print data['data']

    import doctest
#    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
