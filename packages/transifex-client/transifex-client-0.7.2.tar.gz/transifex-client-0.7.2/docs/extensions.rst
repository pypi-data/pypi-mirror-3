Extensions
==========

Extensions should be normal python packages found in the
``PYTHONPATH`` variable. There should be an entry in the
``.transifexrc`` file for each active extension. These entries should
be in the section ``Extensions``.

Each extension **must** have a top-level class named
``Extension``. The ``Extension`` class **must** inherit the
``txclib.extensions.BaseExtension`` class. This class should override
the ``initialize`` method, which will be called by the transifex
client to run any initialization code for the extension. The client
will guarantee that by the time the ``inititalize`` method is run, the
client will be initialized fully. The extension should not assume
anything else (eg about the order of initialization of the
extensions). Thus, any changes the extension makes won't be reverted
by the initialization code of the client.

Additionally, the module should have a top-level docstring, which
could be used for documentation and a ``NAME`` variable.

Also, each extension will have **read** access to the ``.transifexrc``
configuration file and **read/write** access to the section named as
``NAME``.

There will be two ways that an extension can interact with the client:
through signals and through an inheritance-based interface and a
centralized registry (*Factory Design Pattern*).

Signals
-------

Use signals to notify for certain actions:

- Program initialization
- Configuration reading
- Parameters setup
- Parameters processing
- Project created
- Project saved
- Resource created
- Resource saved
- Translation pulled
- Translation pushed
- All translations pulled
- All translations pushed
- Source file pulled
- Source file pushed
- About to be terminated

For example, there is a request from Joomla! folks in GS about
automatic packaging of the translations. This could be implemented as
an extension which listens to the ``translations_pulled`` signal and
automatically creates the package Joomla! developers need.

Registry
--------

Use a global ``Registry`` class to register the class that handles
each functionality. This allows extensions to register their own
handlers for each action.

This gives extra possibilities for extensions. For example, there is a
ticket (http://trac.transifex.org/ticket/739) about the client not
verifying SSL certificates. This functionality depends on the M2Crypto
module, which (since it is not part of the standard library) we do not
want to have a dependency on. This problem could be solved with an
extension, which would inherit the normal URL handler class and use
the M2Crypto package to verify the SSL certificate first.
