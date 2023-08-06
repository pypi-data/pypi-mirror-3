.. Commandeer documentation master file, created by
   sphinx-quickstart on Tue Sep  4 01:20:31 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Commandeer's documentation!
======================================

Commandeer is a command-line generator library that you can use to add a nice command line interface to your python programs.

It will take care of parsing all command line options as well as calling the right command functions in your script. And it will generate a nice-looking help for the program and for each of the commands.

We've written Commandeer in such a way that it should work just like you expect it to. There are only two things you need to do:
 * name the functions you want to expose on the command line to end in ``_command``.
 * Add the following code snippet to the end of your command line module::
   
     import commandeer
     if __name__ == '__main__':
         commandeer.cli()

You should try it out!

However, if you you're new to Commandeer, you can also continue with our :doc:`tutorial. <quickstart>`

Or have a look at the :ref:`example containing everything. <total-example>`

Or, if you're looking for specific information, have a look at the :doc:`feature documentation. <features>`

.. raw:: html

   <hr />

As a quick start, here's how a sample script could look like [#f1]_:

.. literalinclude:: ../samples/sample.py

And what does that give us? Have a look at the following session to get a feeling for the result:

.. code-block:: none

  $ python sample.py
    This is a sample script that shows two commands and how to call them from Commandeer.
    Usage: sample.py command [options]

    Here are the commands you can try:

      help      Show this help screen.
      log       Outputs the input, with an optional timestamp and some indenting.
  
    If you need help on any of them, try "sample.py help command" for any of them.
  $ python sample.py log info "Hello World"
  [2012-09-06 12:41:00.157822] [info] Hello World
  $ python sample.py log warn "ions destabilized" --indent 2
    [2012-09-06 12:41:15.924351] [warn] ions destabilized
  $ python sample.py log warn "ions destabilized" --indent 2 --notimestamp
    [warn] ions destabilized
	
In short, it will give you:
 * a help message that is output when you call your program without arguments or with the single argument `help`
 * command matching: the first argument that does not start with ``-`` selects the function you want to call
 * argument matching: all arguments that do not start with `-` get passed to your program as arguments
 * keyword matching: all arugments that start with `-` get passed to your program as switches. The number of dashes is ignored.


License
=======

Copyright (C) 2012 Johannes Spielmann

Commandeer is licensed under the terms of the GNU General Public Licenses as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

For a full description of the license, please see the file

  LICENSE
  
as included with the source distribution of Commandeer.

.. toctree::
   :hidden:
   
   contents

.. rubric:: footnotes
.. [#f1] You can find this and all other sample programs in the folder ``samples`` in the Commandeer source code.
