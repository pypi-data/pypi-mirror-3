.. _overview:

Overview
========

A distributed environment controlled by ``PPlus`` (mainly inherited from
`Parallel Python <http://www.parallelpython.com/>`_) is composed of a
set of machines (**nodes**) that offer their resources to execute assigned
tasks.
All those **nodes** are running the ``pplusserver.py`` process in the background,
that provides visibility over the local network of a prefixed number
of computational **workers** and controls all data transfers
(see :ref:`using`).

The Python code to be executed by ``PPlus`` consists of the following
conceptual pieces:

- the **worker** code is distributed over the network to the **node** machines
  to be executed there; it produces `partial` results saved locally and ready
  to be collected
- the **master** code that distributes the **worker** code pieces, collects all
  `partial` results and produce **master** (final) results

When a Python code needs to be executed in parallel, it is placed on one of the
machines. That process is designated to be the **master** process: it distributes all
parallel tasks to node **workers** and it receives all the results.
Note that the machine running the master process can also provide workers
(running the ``pplusserver.py`` script).

.. image:: _static/example.png
   :align: center

Both **worker** code and **master** code can do any computations, import modules
(with some restrictions), and produce files.



.. rubric:: Experiments

Internally, ``PPlus`` uses the concept of **experiments** to organize the code
and data.
The **experiment** consists of the code that performs a specific task,
including pieces to be executed in parallel (i.e. master code and all worker
code), as well as all regular files produced by that code. A single instance of
the worker code, submitted for remote execution, is also called `worker task` or
`worker job`.

To ease running of multiple subsequent experiments over the network, the
experiment code can use a **shared file system resource** to store files
produced during execution and to access them back if needed.
This functionality is controlled by ``PPlus`` in a transparent way and it is
exposed through a simple :ref:`API <pplusconn>`.

.. note::

    PPlus controls shared disk resource in the form of any network-mounted file
    system
    (e.g. `NFS <http://en.wikipedia.org/wiki/Network_File_System_%28protocol%29>`_,
    `Samba <http://en.wikipedia.org/wiki/Samba_%28software%29>`_ etc.), that
    can be accessed as normal directory. As a result, PPlus manipulates all
    remote file system resources as normal files and directories.

.. warning::

    PPlus has been developed on Linux utilizing single NFS-mounted external disk
    as shared file system resource; using of different remote file systems and
    different operating systems has not been tested at this moment.


The `experiment code` can access and store any remote files in a dedicated
**experiment directory**, created specifically for that purpose on the
**shared disk** resource.
Both experiment master code and all worker code have an access to the
experiment directory. The files produced by different experiments are physically
separated; no direct support is provided for accessing data from outside the
experiment. As a result, many experiments can run simultaneously without data
corruption.

.. note::

    The `experiment directory` is created automatically when the
    `experiment code` is started. It is possible to assign already existing
    directory passing manually an experiment id, but is responsibility of the
    user code to manage results collected in different run to avoid unexpected
    data corruptions or overwriting.


.. rubric:: Sessions

Each execution of the code, of both master and worker type, on each machine,
is considered a **session**. All the activity during a session is stored in a
separated session log file. More specifically:

- all worker tasks are considered running in separate sessions, and will produce
  separate session log files;
- the `master code` is also treated as running in separate session, but it will
  produce **two** logs; `session log` documents the activity regarding accessing
  shared disk resource from within master code; `experiment log` documents the
  activity regarding distribution of worker tasks; see
  :ref:`logging` for more details.
