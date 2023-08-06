
Feature overview
================

This section lists all features of Commandeer and how to access them. The list is alphabetical, and thus not well-suited to discovering available features. If you're looking for an easily learnable list of features you should try out :doc:`the tutorial <quickstart>`.

All features in Commandeer can be combined with every other.

All scripts featured in this document are available as source from the ``samples/`` directory in the source distribution of Commandeer.


Aliases
-------

Aliases are alternative names for your commands. They work in any place where the command name works, too.

The aliases will show up in the help for an individual command, but not in the general help. You can attach one or more aliases to a command by setting the ``aliases`` property of the function object directly. Make sure that it is iterable!

.. literalinclude:: ../samples/feature-alias.py


.. _commands:

Commands
--------

To make a function available as a command for the command line, it has to be in the local name space with a name ending in ``_command``.

The ending allows you to use Python's reserved words as command names, as well as add utility functions to your namespace that you don't want to export to the command line.

.. literalinclude:: ../samples/feature-commands.py


.. _commanddoc:


Command documentation
---------------------

For each command that you expose, two different help locations are created: the general help for the program and the help for specific commands. These are available from the command line as ``script.py help`` and ``script.py help commandname``, respectively. For both these help documentations, the docstring of the function is used. The short documentation is created from the first line of the docstring, the longer documentation uses the whole docstring (without :ref:`parameter descriptions <paramdoc>`, as outlined below).

.. literalinclude:: ../samples/feature-command-doc.py


Module documentation
--------------------

In addition to the :ref:`help documentation for individual commands <commanddoc>`, you can add a help documentation to your program. This is simply the docstring for the module that you're using as your command line entry point. It can be as long as you want it to be and should describe the function of the program.

The documentation for your program will be printed at the top of the general help documentation.

.. literalinclude:: ../samples/feature-module-doc.py


.. _command-line-switches:

Command line switches
---------------------

You can add command line switches to your program by simply giving a command function an argument with a default value.

The given command line switches will be parsed and Commandeer will try to convert them to the right type (int, float, boolean or string).

Commandeer will accept command line switches in several different formats, as illustrated in the session below.

.. literalinclude:: ../samples/feature-switches.py

.. warning:: Remember: don't trust the input you get! Malicious users will try to pass stuff that breaks your program or makes it misbehave. Therefore: always sanitize your input before using it!

Note that Commandeer will *try* to convert the input into the correct type, but you'll get the raw string if it cannot do the conversion, as shown in this session:

.. code-block:: none

  $
  $ python feature-switches.py test
  boole=True, number=0, value=''
  $ python feature-switches.py test --boole
  boole=True, number=0, value=''
  $ python feature-switches.py test --boole
  boole=True, number=0, value=''
  $ python feature-switches.py test --noboole
  boole=False, number=0, value=''
  $ python feature-switches.py test --boole=False
  boole=False, number=0, value=''
  $ python feature-switches.py test --boole=True
  boole=True, number=0, value=''
  $ python feature-switches.py test --boole no
  boole=False, number=0, value=''
  $ python feature-switches.py test --number 1
  boole=True, number=1, value=''
  $ python feature-switches.py test --number=1.5
  boole=True, number=1.5, value=''
  $ python feature-switches.py test --number='not a number'
  boole=True, number='not a number', value=''
  $ python feature-switches.py test --value "value"
  boole=True, number=0, value='value'
  $ python feature-switches.py test --value "two words"
  boole=True, number=0, value='two words'
  $ python feature-switches.py test --value "two words" not a value
  Error: too many arguments. Here is a list of arguments this command takes and the values you gave for them:

  You supplied the additional arguments: not a value
  Try 'help test' for a full documentation of this command.



.. _paramdoc:

Documentation for switches and arguments
----------------------------------------

You can add documentation for each of your arguments and command line switches by using a strict subset of the `epydoc <http://epydoc.sourceforge.net/manual-fields.html>`_ or `doxygen <http://www.stack.nl/~dimitri/doxygen/commands.html#cmdparam>`_ parameter documentation format.

Each parameter documentation must be in the format of one of these lines::
 
  @param name documentation
  \param name documentation

The parameter documentation will show up in the help documentation for specific commands.

.. literalinclude:: ../samples/feature-param-doc.py


.. _varargs:

Optional command arguments
--------------------------

In addition to :ref:`command line switches <command-line-switches>` and :ref:`required arguments <required-arguments>` your command function can accept an variable number of arguments. These are modelled by adding a ``*varargs`` parameter to your functions.

All arguments that cannot be matched to any of the required arguments will be added to the varargs. No type conversion will be done for these arguments, so you will get a list of strings. The list may be empty.

.. literalinclude:: ../samples/feature-varargs.py

.. warning:: Remember: don't trust the input you get! Malicious users will try to pass stuff that breaks your program or makes it misbehave. Therefore: always sanitize your input before using it!


.. _required-arguments:

Required command arguments
--------------------------

Any non-keyword (and non-default) parameters for your command functions will be interpreted as a required argument. Commandeer accepts any item from the command line that does not start with ``-`` or is preceded by an item that starts with a ``-`` and does not contain an equals sign as an argument. The arguments are passed to your function in the order in which they appear in the command line.

All arguments are passed as strings as they appear in the command line.

If there are too few or too many arguments on the command line (and no :ref:`variable number of arguments <varargs>` is specified), Commandeer will output an error message and the help documentation for the called command.

.. literalinclude:: ../samples/feature-arguments.py

.. warning:: Remember: don't trust the input you get! Malicious users will try to pass stuff that breaks your program or makes it misbehave. Therefore: always sanitize your input before using it!


Short command versions
----------------------

Commandeer automatically accepts shortened command names, as long as they are uniquely recognizable. These short commands are simply prefixes of your command names.

You can see how this works in the following demo session. For source code refer to the :ref:`commands documentation <commands>`.

.. code-block:: none

  $ python feature-commands.py class
  class
  $ python feature-commands.py clas
  class
  $ python feature-commands.py cla
  class
  $ python feature-commands.py cl
  class
  $ python feature-commands.py c
  class
  $ python feature-commands.py test
  test
  $ python feature-commands.py tes
  test
  $ python feature-commands.py te
    Usage: feature-commands.py command [options]

    Here are the commands you can try:

      class      
      help       Show this help screen.
      test       
      text       
  
    If you need help on any of them, try "feature-commands.py help command" for any of them.
  Error: Command 'te' not found