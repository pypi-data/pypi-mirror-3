
=======================
Working with Converters
=======================

Converters are deceptively simple.

You may know that JSON plays well with a limited set of value types. ConfigViper
just provides a way to work easily with Python dictionaries. For persistence,
ConfigViper stores your configuration values to a file in JSON format. Why JSON?
Because JSON is a portable format, it is human readable and can be easily edited
with any text editor.

So you'll need converters if you want to store more sofisticated Python types,
like dates, times, decimal values (not only floats), or whatever type you can 
convert from Python to a type JSON can handle. A converter is a simple Python
class with two methods: ``to_python`` and ``to_json``. Convertes works on a per
config-path basis. This means that you can have a specialized converter for a
complex type for an specific config-path.


Built-in Converters
-------------------

ConfigViper comes with built-in converters for 
date (:class:`~configviper.converters.DateConverter`), 
time (:class:`~configviper.converters.TimeConverter`), 
datetime (:class:`~configviper.converters.DatetimeConverter`) and
decimal (:class:`~configviper.converters.DecimalConverter`) objects. You can
refer to :doc:`api` for details on these converters. The ``converters``
module also offers instances of these built-in converters as
:attr:`~configviper.converters.DATE_CONVERTER`,
:attr:`~configviper.converters.DATETIME_CONVERTER`,
:attr:`~configviper.converters.DECIMAL_CONVERTER`, and
:attr:`~configviper.converters.TIME_CONVERTER` constants.


Building Your Own Converters
----------------------------

Any class should act as a converter. It just needs to provide two methods, one
called ``to_python`` and another called ``to_json``. By the way, a converter
can inherit from :class:`~configviper.converters.Converter`, but it's not a
requirement and your class will not gain anything by doing this (as I said,
converters are deceptively simple).

The ``to_json`` method should convert your Python type to a type JSON can
handle. You can serialize your Python type to a string, for example, or you
can return a dictionary with types JSON can handle. The ``to_python`` method
should convert your JSON value back to your Python type. Let's build a
converter for a ``Person`` class:

.. code-block:: python

    class Person(object):
        
        name = ''

        age = 0

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

        def __repr__(self):
            return '%s, %d years old' % (self.name, self.age)


For this example we'll convert our ``Person`` instances to Python dictionaries,
where each key with a value JSON can handle (string for the name and integer 
for the age attribute):

.. code-block:: python

    from configviper import converters

    class PersonConverter(converters.Converter):
        def to_json(self, value):
            # value should be an instance of Person
            return { 'name': value.name, 'age': value.age }
        
        def to_python(self, value):
            # value will be deserialized from JSON as a Python dictonary
            # just like the returned by to_json method
            return Person(**value)


Now you can apply your converter to a config-path on stabilization, like this:

.. code-block:: python

    from configviper import ConfigViper

    values = (
        ('sys.owner', Person(name='John Doe', age=37), PersonConverter(),),)

    conf = ConfigViper()
    conf.stabilize(values)

    print conf.sys.owner
    # expected "John Doe, 37 years old"
        
    conf.set('sys.owner', Person(name='Alice Foo', age=25))
    
The resulting configuration file should looks like:

.. code-block:: json

    {
        "sys": {
            "owner": {
                "name": "Alice Foo",
                "age": 25
            }
        }
    }
    