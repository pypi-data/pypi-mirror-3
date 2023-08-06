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

    ConfigViper.configure()

    conf = ConfigViper()
    conf.set('spam.ham.eggs', 'sausage')

And the JSON file will looks like (``~/.configviper/configviper.json``):

.. code-block:: json

    {
        "spam": {
            "ham": {
                "eggs": "sausage"
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
#. Small and really simple.


Installation
------------

Install ConfigViper using ``pip install ConfigViper`` command. If you downloaded
the sources from `PyPI`_ go to ``ConfigViper-<version>`` directory and type
``python setup.py install`` command. You can also get the sources from
`BitBucket`_ repository (you will need `Mercurial SCM`_ installed on your
system)::

    hg clone https://bitbucket.org/danielgoncalves/configviper


Documentation
-------------

.. toctree::
   :maxdepth: 2

   usage
   converters
   api


Change History
--------------


Version 0.1
^^^^^^^^^^^

* Released 12 march 2012.


Version 0.2
^^^^^^^^^^^

* Released 18 march 2012;
* Documentation hosted on PyPI.


Version 0.3
^^^^^^^^^^^

* Released 14 april 2012;
* Default config-path separator changed from ``/`` to ``.``;
* Configuration values can be accessed like object attributes::

    # using the get() method
    conf.get('spam.ham.eggs')

    # or like object attributes
    conf.spam.ham.eggs


Version 0.3.1
^^^^^^^^^^^^^

* Released 18 april 2012;
* [FIXED] No conversion was happening when config-paths are
  accessed like object attributes;
* Only one proxy instance is created when accessing config-paths
  like object attributes;
* Some more unit tests added.


Version 0.4
^^^^^^^^^^^

* Released 25 april 2012;
* [ADDED] Stop saving (or bulk set) feature;
* [ADDED] Backup before save with automatic restore on failure (optional).


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _`Python`: http://www.python.org/
.. _`JSON`: http://www.json.org/
.. _`PyPI`: http://pypi.python.org/pypi/ConfigViper
.. _`BitBucket`: http://www.bitbucket.org/
.. _`Mercurial SCM`: http://mercurial.selenic.com/
