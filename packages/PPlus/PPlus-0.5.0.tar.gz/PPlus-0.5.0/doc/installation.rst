.. _installation:

Installation
============
``PPlus`` is available on `PyPI <http://pypi.python.org/pypi/PPlus>`_
and may be easily installed using standard python setup tools like
`pip <http://www.pip-installer.org/>`_ or
`easy_install <http://packages.python.org/distribute/easy_install.html>`_.

Anyway, we recommend to install ``PPlus`` from the
`source distribution <https://bitbucket.org/slipguru/pplus/downloads>`_,
to also get some useful configuration files and testing scripts
shipped with it.

After extracting the compressed package, you can use the default
distutils commands::

    $ python setup.py install

After installation, you can launch the test suite::

    $ python -c "import pplus; pplus.test()"

.. note::

    Tests will print reports of expected raised exceptions.
    Check if you get ``OK`` or ``FAILED`` status at the end.

.. note::
    You have to install ``PPlus`` on **each machine** you would like to use
    as a node worker and /or  master.

You can also check the latest sources on ``PPlus``
`code repository <https://bitbucket.org/slipguru/pplus>`_::

    $ hg clone https://sabba@bitbucket.org/slipguru/pplus


.. _configuration:

Configuration
-------------
``PPlus`` uses a configuration file that specifies the paths for storing
and managing remote and temporary files and logging.
Each machine that participates in the network should provide its own
configuration file.

During the installation, a default configuration file is saved in
``/etc/pplus/pplus.cfg``. The simplest way to configure ``PPlus`` is to
edit this file which will be reached by master and workers scripts on the
machine.

On the master process, the configuration file may be specified directly
in ``config_file_path`` parameter when
instantiating :class:`~pplus.PPlusConnection`::

    pc = PPlusConnection(config_file_path='pplus.cfg')

If not specified that way (and in all worker sessions), ``PPlus`` looks for the
configuration file in the following locations, in order:

1. current working directory, as obtained by :py:func:`os.getcwd`

2. ``~/.pplus/pplus.cfg``, e.g. ``/home/user/.pplus/pplus.cfg``

3. global configuration file ``/etc/pplus/pplus.cfg`` installed with ``PPlus``
   (recommended)

.. note::
    On workers, current working directory depends on how ``pplusserver.py``
    script is executed.

An example of standard configuration file can be found in the source distribution
of ``PPlus`` under ``<path-to-pplus-source>/examples/pplus.cfg``
or :download:`downloaded here <../examples/pplus.cfg>`:

.. literalinclude:: ../examples/pplus.cfg
   :language: ini

The ``DISK_PATH`` is the root of remote file system resource controlled by
``PPlus`` (e.g. the NFS mount point).

The ``CACHE_PATH`` is the root directory of internal local cache used by
``PPlus``.

The ``CACHE_WAITING_TIME`` is the time between locking individual file objects
managed in local cache of the machine, to avoid any possibility of concurrent
writing. This parameter may be configured individually for each machine,
if needed.

The ``SESSION_LOG_LEVEL`` is the level of detail for log files produced by worker
code on worker machines during execution of worker tasks, as well as the
`session log` produced by master code on master machine.

The ``JOB_MAX_RESUBMISSION`` is the number of maximal re-submissions of single
failed worker task. That is, if the worker task has failed, it will be
submitted, possibly to different machine, to be executed again. If it fails again,
it will be submitted back again etc, maximum up to the number of times specified
by this parameter.

The ``EXPERIMENT_LOG_LEVEL`` is the level of detail for `experiment log` produced
by master code on master machine.

.. note::

    (`OS Specific`) All mount points specified in ``DISK_PATH`` on all
    machines participating in the single experiment, must point to the **same**
    physical location on disk resource. Consult the documentation specific
    for your OS for more details.

.. note::

    The ``CACHE_PATH`` must be writable by the user that will execute
    master/worker code on that machine.


Configuration options in debug mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``PPlus`` has also a debug running mode::

    pc = PPlusConnection(debug=True)

When a :class:`~pplus.PPlusConnection` is instantiated in this way no
connection between master a worker processes is created and each configuration
option assume its default value (e.g. ``JOB_MAX_RESUBMISSION=0`` and
``CACHE_WAITING_TIME=2``).
Tasks will be executed on the local machine, creating a number of subprocesses
equal to the number of cpu cores minus one.
Moreover, two local (w.r.t. master process working directory) directories,
namely ``disk`` and ``cache``, will be created to *simulate* shared disk and
local cache spaces.


.. _test:

A simple Task: counting words in a text file
--------------------------------------------
With the source distribution of ``PPlus`` it is also shipped a simple example of
how ``PPlus`` could be use. This script is also useful to test the installation
and the definition of a valid configuration file and can be
found under ``<path-to-pplus-source>/examples/pplus_test.py`` or
:download:`dowloaded here <../examples/pplus_test.py>`.

The script defines a job function ``count`` which relies on a smaller function
``count_word``.

.. note::

    A ``PPlus`` job function has to expect as first argument a
    :class:`~pplus.PPlusConnection` instance (automatically created
    by ``PPlus``)


.. literalinclude:: ../examples/pplus_test.py
   :lines: 7-20

Into the main function is first created a new ``PPlus`` connection:

.. literalinclude:: ../examples/pplus_test.py
   :lines: 22-26

Because a :class:`~pplus.PPlusConnection` instance is created in debug mode,
no configuration file is needed.

Then, if you have an active Internet connection, the script will automatically
download a sample text file, namely ``bigfile.txt``, which can also
be downloaded manually from
`the repository <https://bitbucket.org/slipguru/pplus/downloads/bigfile.txt>`_,
and put it on the shared disk space:

.. literalinclude:: ../examples/pplus_test.py
   :lines: 28-36

We are now ready to submit the jobs. The target is to count how many times
a prefixed set of (actually 6) words appear into the text contained in
``bigfile.txt``:

.. literalinclude:: ../examples/pplus_test.py
   :lines: 38-41

Then we can collect and print the results:

.. literalinclude:: ../examples/pplus_test.py
   :lines: 43-47

From the ``PPlus`` source dir, if you run::

    $ examples/pplus_test.py

the expected results is something like:

.. program-output:: ../examples/pplus_test.py

Because we are in debug mode, jobs have run on the local machine cpus and
you should have, in the current working directory, two new directories
simulating local cache (``cache``) and shared disk (``disk``):

.. command-output:: ls cache disk

Each one contains a sub-directory named as the executed ``experiment id``.

The **shared disk** ``disk`` contains the ``BIGFILE`` which was putted in,
and an *experiment log* ``experiment.log``:

.. command-output:: ls -R disk


The **local cache** contains the ``BIGFILE`` which was got by the workers,
into the job function, and a ``logs`` directory containing logs for
each ``PPlus`` session:

.. command-output:: ls -R cache

Because the experiment ran in debug mode, here we have logs for all
sessions:

* one for the master: ``hostname.master.<session_id>.log`` and
* one for each of (6) workers: ``hostname.worker.<session_id>.log``.

Now we are ready to configure our network and run the experiment
on a distributed environment as described in :ref:`using`.
