.. _using:

Using PPlus
===========

In :ref:`test` you can see how to use ``PPlus`` in a parallel but not
distributed environment (*debug mode*, see also
:class:`~pplus.PPlusConnection` arguments).

In this section we assume you have correctly edit a ``PPlus`` configuration
file adding valid disk and cache paths, as explained in :ref:`configuration`.

To run the test distributing the tasks we have only to start a
``pplusserver.py`` in auto-discovery mode (see :ref:`server`)::

    $ pplusserver.py -a

and then the ``pplus_test.py`` script shutting-off the debug modality::

    pc = pplus.PPlusConnection(debug=False) # line 24 of pplus_test.py


.. _server:

PPlus Server options
--------------------
Executing ``pplusserver.py`` with the ``--help`` option::

    $ pplusserver.py --help

you get a complete list of options (see also :class:`~pplus.PPlusConnection`):

.. program-output:: ../scripts/pplusserver.py --help


.. _slipguru_env:

Example: a working environment
------------------------------
To facilitate computational experiments performed by Computational Biology
and Biostatistics branch of `SlipGURU <http://slipguru.disi.unige.it/>`_
research group, a complete environment for parallel computations was created
in our lab.

It consists of a few personal Linux workstations, accessing each other in
within the same local network.
A separate workstation has been dedicated to provide only the external disk
space, accessible via NFS.

On all participating workstations, running various flavors of Ubuntu, a
dedicated login-less user ``pplus`` was created and a system service
(``pplus_services``) was installed on each
participating workstation, that mounts external disk via NFS and starts
``pplusserver.py``, so the machine can re-enter the environment automatically
even after manual restart.

The NFS mount point and location of local cache are in ``pplus`` home directory,
and user ``pplus`` will execute any incoming worker code.

Master code of the experiment can be executed on any workstation from any user.

All the operation needed to install a compete environment are performed using
the :download:`pplus_add_node.py <../install/pplus_add_node.py>` script
shipped with ``PPlus``
`source distribution <https://bitbucket.org/slipguru/pplus/downloads>`_ into
the ``install`` directory together with the
:download:`pplus_services <../install/pplus_services>` Linux script.
Run::

    $ pplus_add_node.py --help

to see all the options:

.. program-output:: ../install/pplus_add_node.py --help
