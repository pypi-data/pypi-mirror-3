.. _pplusconn:

PPlusConnection class
=====================
.. module:: pplus

.. autoclass:: PPlusConnection
   :members: put, remove, get_path, write_remotely, submit, collect

   .. rubric:: Attributes

   .. autosummary::

      ~PPlusConnection.id
      ~PPlusConnection.session_id
      ~PPlusConnection.is_debug
      ~PPlusConnection.disk_path
      ~PPlusConnection.cache_path
      ~PPlusConnection.session_logger

   .. rubric:: Members

   .. autosummary::

      ~PPlusConnection.put
      ~PPlusConnection.remove
      ~PPlusConnection.get_path
      ~PPlusConnection.write_remotely
      ~PPlusConnection.submit
      ~PPlusConnection.collect

.. autoexception:: PPlusError


Utility functions and classes
=============================

Logging
-------
.. module:: pplus.loggers

.. autoclass:: PPlusLogger

Local Cache
-----------
All the functions working on the local cache rely on a file system locker
(mutex) to avoid file corruption during concurrent operations.

.. module:: pplus.lockfile
.. autoclass:: FilesystemLock

.. module:: pplus.ioutils
.. autoclass:: PPlusTemporaryCachedFile
.. autofunction:: copy_if_not_exists
.. autofunction:: remove_if_exists
.. autofunction:: create_local_experiment_dirs

Configuration file
------------------
.. autofunction:: read_config_file
