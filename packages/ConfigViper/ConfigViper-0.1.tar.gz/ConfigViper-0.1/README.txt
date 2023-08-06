
===========
ConfigViper
===========

ConfigViper is a set of `Python`_ classes for handling configuration files
saved in `JSON`_ format. For example::

    from configviper import ConfigViper
    conf = ConfigViper()
    conf.set('a/b/c', 'd')

And the JSON file will looks like::

    {
        "a": {
            "b": {
                "c": "d"
            }
        }
    }

Goals
-----

#. Simple to define default values (avoiding "defaults" everywhere);
#. Simple to write converters between Python and JSON types (even for complex 
   Python types);
#. Human editable format (JSON is readable enough);
#. Portable configuration format (JSON is portable enough);
#. Easy to add configuration options without destroying existing ones;
#. Accessible anywhere in the app code (avoiding singleton's boring discussions);
#. Small and simple to be written by me (so anyone can use/contribute and/or
   point my faults).

More Documentation
------------------

For usage example and more information, please refer to the documentation,
available in the ``doc`` directory. There's also a built documentation set
packaged and available for download at 
`downloads page <https://bitbucket.org/danielgoncalves/configviper/downloads>`_.


Licensing
---------

ConfigViper is licensed under GNU's `LGPL`_.


.. _`Python`: http://www.python.org/
.. _`JSON`: http://www.json.org/
.. _`LGPL`: http://www.gnu.org/licenses/lgpl.html
