Features
========

- Language mappings
- Support for different servers
- Support for SSL encryption
- Push source file
- Push translations
- Pull source file
- Pull translations
- Support for Python 2.5 and later
- Keep configuration file format
- Keep logs
- Verbose/quiet mode
- Trace of all actions in debug messages
- Support for extensions
- Support windows
- Support scripting:
  + Specific input and output


Configuration files
===================

.transifexrc
------------

- Keep sections for each server encountered (authentication info).
- Have an ``Extensions`` section.
- Have a section for each extension.
- General options (eg enforce SSL)


.tx/config
----------

- Have host name to query for the project.
- Have one section per resource (as is today)


Design
======

Command-line options
--------------------

 - ``init``
 - ``set``
 - ``push``
 - ``pull``
 - ``help``
 - ``status``
 - ``delete``


Internals
---------

.. image:: class_diagram.png
