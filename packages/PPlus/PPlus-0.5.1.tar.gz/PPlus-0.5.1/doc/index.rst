============================================================
PPlus - A Parallel Python Environment with easy data sharing
============================================================

:Release: |release|
:Homepage: http://slipguru.disi.unige.it/Software/PPlus
:Repository: https://bitbucket.org/slipguru/pplus

**PPlus** is a simple environment to execute Python code in parallel on many
machines without much effort.
It is actually a fork of `Parallel Python <http://www.parallelpython.com/>`_,
another simple but powerful framework for parallel execution of python code,
which lacks features needed for effective use in our daily research.

More specifically, ``PPlus`` was created to answer following needs:

- to facilitate data transport over distributed environment of usually
  very big file, exposing a simple interface while handling details
  in the background

- to separate file handling between different experiments, so one machine can
  participate in many computational experiments simultaneously


User documentation
==================
.. toctree::
   :maxdepth: 2

   overview.rst
   installation.rst
   using.rst
   insight.rst


.. _api:

PPlus API
=========
.. toctree::
   :maxdepth: 3

   api.rst

Quick Reference
---------------
.. currentmodule:: pplus

.. autosummary::

   pplus.PPlusConnection
   pplus.PPlusError
   pplus.loggers
   pplus.ioutils
   pplus.lockfile


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
