.. ConfigViper documentation master file, created by
   sphinx-quickstart on Sat Mar 10 20:05:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ConfigViper
======================

ConfigViper is a set of `Python`_ classes for handling configuration files
saved in `JSON`_ format. For example:

.. code-block:: python

    from configviper import ConfigViper
    conf = ConfigViper()
    conf.set('a/b/c', 'd')

And the JSON file will looks like:

.. code-block:: json

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

Contents
--------

.. toctree::
   :maxdepth: 2

   usage
   converters
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`Python`: http://www.python.org/
.. _`JSON`: http://www.json.org/
