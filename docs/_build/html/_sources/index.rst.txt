.. Advanced RSync documentation master file, created by
   sphinx-quickstart on Sun Jan  8 22:55:37 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Advanced RSync's documentation!
==========================================

About Advanced RSync
====================
Advanced RSync is a command-line application that targets to syncronize storage locations of different type by creating a
list of common functionalities in manipulating files. The motivation of the project comes from the
need of a common format that makes syncing different storage locations an automatically done job and
is meant to ease the refresh of a location with the most relevant files by modification time.
Application can be easily extended by implementing the contract of the FileStorage class and
taking advantage of the methods created especially for extension of the Algorithm. One can contribute
to the project by adding unsupported formats at the internal strucure level of each package (including parsing-level).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
