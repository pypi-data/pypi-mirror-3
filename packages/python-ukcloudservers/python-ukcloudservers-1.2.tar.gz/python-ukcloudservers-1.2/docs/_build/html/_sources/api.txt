The :mod:`ukcloudservers` Python API
==================================

.. module:: ukcloudservers
   :synopsis: A client for the Rackspace Cloud Servers API.
   
.. currentmodule:: ukcloudservers

Usage
-----

First create an instance of :class:`CloudServers` with your credentials::

    >>> from ukcloudservers import CloudServers
    >>> ukcloudservers = CloudServers(USERNAME, API_KEY)

Then call methods on the :class:`CloudServers` object:

.. class:: CloudServers
    
    .. attribute:: backup_schedules
    
        A :class:`BackupScheduleManager` -- manage automatic backup images.
    
    .. attribute:: flavors
    
        A :class:`FlavorManager` -- query available "flavors" (hardware
        configurations).
        
    .. attribute:: images
    
        An :class:`ImageManager` -- query and create server disk images.
    
    .. attribute:: ipgroups
    
        A :class:`IPGroupManager` -- manage shared public IP addresses.
    
    .. attribute:: servers
    
        A :class:`ServerManager` -- start, stop, and manage virtual machines.
    
    .. automethod:: authenticate

For example::

    >>> ukcloudservers.servers.list()
    [<Server: buildslave-ubuntu-9.10>]

    >>> ukcloudservers.flavors.list()
    [<Flavor: 256 server>,
     <Flavor: 512 server>,
     <Flavor: 1GB server>,
     <Flavor: 2GB server>,
     <Flavor: 4GB server>,
     <Flavor: 8GB server>,
     <Flavor: 15.5GB server>]

    >>> fl = ukcloudservers.flavors.find(ram=512)
    >>> ukcloudservers.servers.create("my-server", flavor=fl)
    <Server: my-server>

For more information, see the reference:

.. toctree::
   :maxdepth: 2
   
   ref/index