
=========
yelljfish
=========

yelljfish is a pixel-based, potentially pseudo-random image generator. It is
very simple.

License
=======

yelljfish is free software under the terms of the GNU Affero General Public
License version 3 (or any later version). This is version 0.1.0 of the program.

Contact
=======

The author of yelljfish is Niels Serup. Bug reports and suggestions should be
sent to ns@metanohi.name for the time being.


Installation
============

Dependencies
------------

yelljfish requires libpng. On Debian-based systems, you can install it with
something like this command: ``apt-get install libpng12 libpng12-dev``

Way #1
------
Get the newest version of yelljfish at
http://metanohi.name/projects/yelljfish/ or at
http://pypi.python.org/pypi/yelljfish

Extract yelljfish from the downloaded file, cd into it and run this in a
terminal::

  # python3 setup.py install

Examples are available in the ``examples`` directory.

Way #2
------
Just run this::

  # pip-3.1 install yelljfish

Note that this will not make any examples available.


Use
===

As a command-line tool
----------------------

Run ``yelljfish`` to use it. Run ``yelljfish --help`` to see how to use it.

As a module
-----------

To find out how to use it, run::

  $ pydoc3 yelljfish


Examples
--------

There are a few examples in the ``examples`` directory.


Development
===========

yelljfish uses Git for code management. The newest (and perhaps unstable) code
is available at::

  $ git clone git://gitorious.org/yelljfish/yelljfish.git


This document
=============

Copyright (C) 2011 Niels Serup

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and this
notice are preserved.  This file is offered as-is, without any warranty.
