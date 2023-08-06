
=============
Usage Example
=============

One of the main objectives is that the configuration API should be easy to be
accessed anywhere in the application. Once configured, you access application
configurations by simple importing ConfigViper module and instantiating 
:class:`~configviper.configviper.ConfigViper` class. 

.. code-block:: python

    import os
    from datetime import datetime

    from configviper import ConfigViper
    from configviper.converter import DATETIME_CONVERTER
    from configviper.converter import TIME_CONVERTER

    # configure where the configurations should be loaded/saved;
    # this should be done only once in the host application code
    ConfigViper.configure(
            pathname=os.path.expanduser(os.path.join('~', '.myapp')),
            filename='myapp.json')

    # create an instance of ConfigViper;
    # if configuration file already exists it will be loaded now
    conf = ConfigViper()

When you create an instance of :class:`~configviper.configviper.ConfigViper`
class, current configuration options (called *config-paths*) are loaded and 
available via :meth:`~configviper.configviper.ConfigViper.get` method. 
Part of the application initialization process is to ensure that all 
configuration options (*config-path*) exists and have reasonable default values.
In ConfigViper this process is called configuration stabilization, where you
can define all config-paths needed and their default values, along with
their converters (see :doc:`converters`).

.. code-block:: python

    # the idea is to have one (and only one) place where you can
    # define default values for a config-path (though you can call
    # stabilize method as many times as you want to);
    values = (
            ('path.to.config', 1, None),
            ('path.to.other', 1.2, None),
            ('path.to.another', datetime.now(), DATETIME_CONVERTER),
            ('path.to.something', datetime.now().time(), TIME_CONVERTER),)

    # merge config-paths default values with existing config-paths,
    # preserving current values of existing ones
    conf.stabilize(values)

Now you can use it anywhere in the appliation code. Just import the 
:class:`~configviper.configviper.ConfigViper` class and create an instance to 
use:

.. code-block:: python

    from configviper import ConfigViper

    conf = ConfigViper()
    print conf.get('path.to.config')

Alternatively, you can get config-path values using a more natural way, as if
they are object attributes:

.. code-block:: python

    conf = ConfigViper()
    print conf.path.to.config
    