
Tutorial
========

Welcome to the tutorial for Commandeer. In this tutorial you will learn to make more and more complex commands that can be exposed on the command line, until you have finally used all available features. You can go to the :ref:`example containing everything <total-example>` right now, if you want.

All of the examples shown in here are available from the ``samples/`` folder in the commandeer sources.

First steps: command functions
------------------------------

The first thing you need to know is that you don't really need to do much to expose your program's functions on the command line. There are only two things you need to do:
 * name each function that you want to make available as a command with the ending ``_command``. 
 * add a call to ``commandeer.cli()`` to your program.
 
In the simplest case, your program would look like ``program1.py``:
  
.. literalinclude:: ../samples/program1.py
  
That's all there is to it! Ok, we added the magic line ``if __name__ == '__main__':`` but that was just to make our program importable.

What this simply program will do for you now is to give you a command line that looks like this:

.. code-block:: none

  $ python program1.py 
    Usage: program1.py command [options]

    Here are the commands you can try:

      help         Show this help screen.
      my_func      
  
    If you need help on any of them, try "program1.py help command" for any of them.  $ python program1.py
  $ python program1.py my_func
  this is my function  

Awesome! Simple command line without doing anything special!

Documentation for your commands
-------------------------------

But the help doesn't look nice yet! The help you see when you start your program without any commands is generated from the docstrings in your program, so let's add a few of them in ``program2.py``

.. literalinclude:: ../samples/program2.py

This make the help screen a lot nicer, and we even get help for each command:

.. code-block:: none

  $ python program2.py 
    Show the different uses of Commandeer
    Usage: program2.py command [options]

    Here are the commands you can try:

      help      Show this help screen.
      info      Print some program information
  
    If you need help on any of them, try "program2.py help command" for any of them.
  $ python program2.py help info
  Usage: program2.py info  
    Print some program information

    At the moment, this is pretty empty, but we will expand upon that in the future!

Now, let's add a few parameters!


Optional parameters
-------------------

Any parameters that have defaults in your functions will be automatically mapped to command line switches, as in ``program3.py``

.. literalinclude:: ../samples/program3.py

Let's try it out:

.. code-block:: none

  $ python program3.py info
  This is my advanced info function
  $ python program3.py info --extrainfo
  This is my advanced info function
  Extra info was requested. The extra info is:
  I am talking to myself, who is 30 years old
  $ python program3.py info --showdate --extrainfo --age=45 --name John
  This is my advanced info function
  Extra info was requested. The extra info is:
  I am talking to John, who is 45 years old
  2012-09-05 13:27:27.047092  

Note that each of the parameters gets their default value if it's not specified on the command line. Also, all parameters are typed, so if your default is a number, you'll get a number, too -- if it can be parsed. If it can't, you'll get the string that was given on the command line.

.. warning:: Remember: don't trust the input you get! Malicious users will try to pass stuff that breaks your program or makes it misbehave. Therefore: always sanitize your input before using it!

Note also that the switch format is pretty flexible. It doesn't care about the number of dashes, whether you use a ``=`` to separate switch and value or a space or the order of the switches.

For switches that have a boolean default value, you also get an extra command line switch that starts with a ``no``. In our example you could have used::
  
  $ python program3.py info --noshowdate

which would be the same as::

  $ python program3.py info --showdate=False



Parameter documentation
-----------------------

Commandeer will automatically generate some help information for the parameters you specified:

.. code-block:: none

  $ python program3.py help info
  Usage: program3.py info  [optional switches]
    Print some program information

    At the moment, this is pretty empty, but we will expand upon that in the future!

    Command line options:  
      --age        
                   default value: 30
      --extrainfo  
                   default value: False
      --name       
                   default value: myself
      --showdate   
                   default value: True

This is nice, but not really that helpful, because we still don't know what these parameters mean. To help with this, you can add documentation for your parameters to your docstring using doxygen or epydoc syntax, with the ``\param`` directive or the ``@param`` directive. There's no difference between the two ways and you can mix them if you wish. Here's how it looks in ``program4.py``:

.. literalinclude:: ../samples/program4.py

And here's how the help looks now:

.. code-block:: none

  $ python program4.py help info
  Usage: program4.py info  [optional switches]
    Print some program information

    At the moment, this is pretty empty, but we will expand upon that in the future!

    Command line options:  
      --age        The age of the person we inform about, part of the extra information.
                   default value: 30
      --extrainfo  Enable extra information.
                   default value: False
      --name       The name we inform about, part of the extra information.
                   default value: myself
      --showdate   Show a timestamp at the bottom of the ouput.
                   default value: True

Required parameters
-------------------

After the optional command line switches, of course there's the option to add required parameters. These are, as in Python, positional arguments to your command function. There's not much else to it, so here's how it looks like:

.. literalinclude:: ../samples/program5.py

The help and error messages will be automatically generated here, too, so we end up with:

.. code-block:: none

  $ python program5.py help info
  Usage: program5.py info type feeling [optional switches]
    Print some program information

    At the moment, this is pretty empty, but we will expand upon that in the future!

    Required arguments:
      type     The type of function that this is.
      feeling  The feeling the function has.

    Command line options:  
      --age        The age of the person we inform about, part of the extra information.
                   default value: 30
      --extrainfo  Enable extra information.
                   default value: False
      --name       The name we inform about, part of the extra information.
                   default value: myself
      --showdate   Show a timestamp at the bottom of the ouput.
                   default value: True

  $ python program5.py info 
  Error: missing required arguments
      type     The type of function that this is.
      feeling  The feeling the function has.
  Try 'help info' for a full documentation of this command.
  $ python program5.py info great
  Error: missing required arguments
      type     'great'
      feeling  The feeling the function has.
  Try 'help info' for a full documentation of this command.
  $ python program5.py info great beautiful
  This is my great info function, it is feeling beautiful
  2012-09-05 21:41:18.301483

It doesn't matter in which order the user passes these arguments to your program -- as long as they are clearly recognizable. Each switch scans the command line for arguments and will accept any string that's written directly after it. For example, this won't work:

.. code-block:: none

  $ python program5.py info --showdate type feeling
  Error: missing required arguments. Here is a list of arguments this command requires and the values you gave for them:
      type     'feeling'
      feeling  The feeling the function has.
  Try 'help info' for a full documentation of this command.


A flexible number of arguments
------------------------------

Sometimes you will want to accept an unknown number of extra arguments, like file names or additional help specifiers. You can do so by using a vararg. Varargs will automatically receive all extra arguments if there are any. If there are no arguments, they will stay empty. Have a look at ``program6.py`` for an example:

.. literalinclude:: ../samples/program6.py

Here's how it would look like on the command line:

.. code-block:: none

  $ python program6.py help echo
  Usage: program6.py echo [optional arguments] 
    Print all the words that were passed on the command line

    This is just a simple echo command.
  $ python program6.py echo hello world
  hello world
  $ python program6.py echo *
  program1.py program2.py program3.py program4.py program5.py program6.py
   
Note in the help the additional ``[optional arguments]``.
  


Aliases
-------

And finally, you can add as many aliases as you want to your commands. These aliases will work in any place where the command name works, too. To attach one or more aliases to a command, simply add them to the function object.

This is illustrated in ``program7.py``:

.. literalinclude:: ../samples/program7.py

Now we can use any of ``redisplay``, ``parrot``, ``reply`` or ``reproduce`` in place of ``echo``.

.. code-block:: none

  $ python program7.py echo hello world
  hello world
  $ python program7.py parrot hello world
  hello world
  $ python program7.py redisplay hello world
  hello world
  $ python program7.py help parrot
  Usage: program7.py parrot [optional arguments] 
    Print all the words that were passed on the command line

    This is just a simple echo command.

You can use this to add names to commands that would not be available as function names in python, like the ``?`` that is mapped to the help command by default:

.. code-block:: none

  $ python program7.py ? parrot
  Usage: program7.py parrot [optional arguments] 
    Print all the words that were passed on the command line

    This is just a simple echo command.

However, you need to make sure that aliases are 

.. _total-example:

A full example!
---------------

So, finally, here is a full example that shows all features. For a description of these features, you can read the tutorial (again) or go the the :doc:`feature overview <features>`. The following script is also included with the Commandeer source code, inside file called ``samples/full.py``. 

.. literalinclude:: ../samples/full.py

To find out what it does, try some of the following:

.. code-block:: none

  $ python sample.py help
    This is a sample script that shows two commands and how to call them from Commandeer.
    Usage: sample.py command [options]

    Here are the commands you can try:

      func      A functional command: adding
      help      Show this help screen.
      log       Outputs the input, with an optional timestamp and some indenting.
  
    If you need help on any of them, try "sample.py help command" for any of them.
  $ python sample.py help log
  Usage: sample.py log logcode [optional arguments] [optional switches]
    Outputs the input, with an optional timestamp and some indenting.

    All of the input arguments are simply output on the standard out. If you specify indenting, the output will be prepended by that number of spaces. If you set timestamp to True, the output will be prepended by '[timestamp] ' for fun.

    Required arguments:
      logcode  The topic or code that this log will be added to.

    Command line options:  
      --timestamp  Add a timestamp to the output. A real timestamp.
                   default value: True
      --indent     The number of spaces the output should be indented by.
                   default value: 0

  $ python sample.py help func
  Usage: sample.py func argument1 argument2
    Aliases: add

    A functional command: adding

    This command works by simply outputting its parameter.

    Required arguments:
      argument1  
      argument2  
  $ python sample.py func 2 3
  5.0
  $ python sample.py add 2.3 abc
  Could not convert arguments to numbers. Please make sure they are in the right format!
  $ python sample.py log warning this is not an argument
  [2012-09-06 00:29:05.489442] [warning] this is not an argument
