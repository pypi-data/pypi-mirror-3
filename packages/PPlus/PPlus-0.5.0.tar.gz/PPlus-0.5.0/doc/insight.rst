.. _insight:

PPlus Insight
=============
In this section we describe some information about PPlus development
that could be useful for advanced users.

.. _file:

File Management
---------------

Remote files are managed based on `file keys`. They serve as identifiers for
accessing physical files without knowing their precise location, regardless of
the network protocols.

The following rules apply to file keys regarding experiment level:

- between different experiment directories, the same file keys may be used;
  that is, key 'BIGFILE' used in experiment A, and key 'BIGFILE' used in
  experiment B, are both referring to two different files
- within experiment directory, if the same file key is used for opening new
  remote file for writing, by default the content of the existing file will be
  overwritten without warning; otherwise, an error will be reported

As a result, **within experiment all file keys must be unique** to avoid
unwanted data corruption.

.. note::

    It is strongly advisable `not` to access any physical files in the locations
    affected by experiment code that is running: `experiment directory` on
    shared disk resource, and `local cache` directories for all participating
    worker machines. Doing so may result in data corruption.

.. note::

    (`OS Specific`) By convention, typical file keys are composed of capital
    letters, digits and underscore, for instance ``CFG``, ``PROBESET_2_GENEID``.
    However, it is possible to use, as file key, any regular file name `that is
    acceptable on the OS that handles shared disk resource`. Consult OS specific
    documentation for more details.

.. note::

    Internally, in the current implementation, the file objects are still
    stored as normal files, and file keys are used as real file names. Therefore,
    knowing the OS specific details of shared disk resource, as well as the file
    keys themselves, it is still possible to access the real file objects, in
    case of untraceable crash.


.. _logging:

Logging
-------

PPlus uses :mod:`logging` to record its activity during the execution of
experiment code.

The following logs are used:

- `experiment log`

This log is created by master code when `experiment ID` is granted. It
documents the activity of the master code regarding control of worker tasks
and interaction with Parallel Python. Also, all errors in worker tasks will be
logged here.
It is considered `private` and is `not` exposed through public :ref:`API <api>`.
When experiment is finished, it is available in the following location::

    <SHARED_DISK_PATH>/<experiment_ID>/experiment.log

- `master session log`

This log is created by master code when `experiment ID` and `session ID` are
granted.
It primarily documents the activity of the master code regarding remote file
access. It is considered `public` and is exposed through public :ref:`API <api>`.
When experiment is finished, it is available in the following location on master
machine::

    <LOCAL_CACHE_PATH>/<experiment_ID>/logs/<machine_name>.master.<session_ID>.log

- `session log`

This log is created by each single worker task, with `experiment ID` given and
`session ID` granted. It documents the activity of the worker code
regarding remote file access. It is considered `public` and is exposed through
public :ref:`API <api>`. When experiment is finished, it is available
in the following location on worker machine::

    <LOCAL_CACHE_PATH>/<experiment_ID>/logs/<machine_name>.worker.<session_ID>.log

.. note::

    Logs produced in ``<LOCAL_CACHE_PATH>`` are never transferred to shared disk
    resource after the experiment has been finished. They must be accessed
    manually on each machine.


.. _execution:

PPlus Execution modes
---------------------

Debug Mode
~~~~~~~~~~
Debug mode is intended to check the correctness of the experiment code, by
executing it as `local experiment`. Instead of distributing worker tasks to
remote machines, all of them will be executed on local machine, along with
master task.

In this mode:

1. PPlus ignores all configuration files and creates ``disk`` and ``cache``
   directories in current working directory::

     >>> import os
     >>> import pplus
     >>> cwd = os.getcwd()
     >>> pc = pplus.PPlusConnection(debug=True)
     >>> os.path.exists(os.path.join(cwd, 'disk'))
     True
     >>> os.path.exists(os.path.join(cwd, 'cache'))
     True

2. The master code is executed normally, and it 'distributes' all worker code
   pieces as usual, producing all regular files normally

3. When any exception is thrown during the execution of master code, the
   experiment code flow is interrupted, and the error is reported

4. When any exception is thrown during the execution of any worker task, the
   task is **not** resubmitted for another execution, the experiment code flow
   is interrupted, and the error is reported


Normal Mode
~~~~~~~~~~~
Normal mode is intended to run the experiment code over fully configured
parallel environment.

In this mode:

1. The master code is executed; during the initial phase, the following specific
   activities occur:

   - the master :class:`~pplus.PPlusConnection` instance is created,
     that reads properly specified configuration file (see :ref:`configuration`),
     obtaining, among others, ``DISK_PATH`` and
     ``CACHE_PATH`` locations `for that particular machine`

   - the experiment ID is granted, in the form of :mod:`uuid`

   - the session ID is granted, in the form of :mod:`uuid`

   - the `experiment directory` is created::

        <DISK_PATH>/<experiment_ID>

     all remote files produced by the whole experiment code will be stored there

   - the `local cache` for the experiment is created on that machine::

        <CACHE_PATH>/<experiment_ID>

     all temporary copies of remote files accessed by master code will be stored
     there

3. The master code continues its execution, eventually worker code pieces are
   distributed over worker machines.
   The master code keeps track of all distributed worker tasks, as well as of
   all completed worker tasks.

4. When some worker piece of code is distributed, together with experiment ID,
   to worker machine, then reconstructed according to Parallel Python rules, and
   started, the following specific activities occur:

   - from within worker code, the worker :class:`~pplus.PPlusConnection` instance
     is created that reads properly specified configuration file, obtaining,
     among others, ``DISK_PATH`` and ``CACHE_PATH`` locations
     `for that particular machine`

   - the experiment ID is re-used to access shared `experiment directory` in::

        <DISK_PATH>/<experiment_ID>

   - the worker session ID is granted, in the form of :mod:`uuid`

   - if does not exists, the `local cache` for the experiment is created for
     that machine::

        <CACHE_PATH>/<experiment_ID>

     all temporary copies of remote files, accessed by any worker code running
     on that machine within the experiment, will be stored there

   - the worker code piece continues its execution until the formal end (i.e.
     when the last statement has been processed, and/or function end has been
     reached)

     .. note::

        When any exception is thrown inside worker task, it is considered an
        `error` and the task is considered as `not completed`. Therefore, all
        worker tasks must be self-contained; deliberate exception propagation
        will lead to error.

     when the execution passes without errors, the worker task is considered
     `completed`

5. Master code, in the meanwhile, controls execution status of all distributed
   worker tasks periodically ('collects' them).

   When some worker task is marked as `not completed`, it is `resubmitted` for
   another execution, until it is marked as `completed`.

   .. note::

        The maximum number of re-submissions is controlled by
        ``JOB_MAX_RESUBMISSION`` parameter, specified for master machine
        (see :ref:`configuration`). Note that by default, the failed worker
        tasks are **not** resubmitted.

   .. note::

        Although the limit of re-submissions is available, the unnecessary
        overhead of computation time is still present for particular long tasks
        (that is, when task is failing constantly because of programming error).
        Therefore, it is advisable to design parallel code with caution using
        `Debug Mode`_, before trying it with `Normal Mode`_.

6. When any exception is thrown during the execution of master code, the
   experiment code flow is interrupted, and the error is reported

7. When master code has collected all distributed worker tasks, it finishes its
   execution until the formal end (i.e. when the last statement has been
   processed, and/or function end has been reached)

8. The experiment code has finished; assuming all configuration files pointed to
   the same shared disk resource, all the shared data are available in one
   `experiment directory`::

         <DISK_PATH>/<experiment_ID>

