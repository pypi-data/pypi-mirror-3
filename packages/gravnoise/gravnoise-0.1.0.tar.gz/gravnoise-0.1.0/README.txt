 
=========
gravnoise
=========

gravnoise is a block-based, gravity-infused puzzle game: it is a bit of a
tetris clone.

It features annoying graphics.


License
=======

gravnoise is free software under the terms of the GNU General Public License
version 3 (or any later version). This is version 0.1.0 of the program.

Contact
=======

The author of gravnoise is Niels G. W. Serup <ns@metanohi.name>. Bug reports
and game suggestions should be sent to him.


Installation
============

Dependencies
------------

gravnoise depends on argparse and pygame. From Python 3.2, argparse is included
in Python. If you're using Python 3.x, x < 2, you can download argparse from
https://code.google.com/p/argparse/

gravnoise will also use the Python packages termcolor and setproctitle
(available at PyPi) if present.

Way #1
------
Just run this::

  # pip-3.1 install gravnoise

  
Way #2
------
Get the newest version of gravnoise at
http://metanohi.name/projects/gravnoise/ or at
http://pypi.python.org/pypi/gravnoise

Extract gravnoise from the downloaded file, cd into it and run this in a
terminal::

  # python3 setup.py install


Use
===

Run ``gravnoise`` to use it. Run ``gravnoise --help`` to check out how to use
it.

As a module
-----------

To find out how to use it, run::

  $ pydoc3 gravnoise


Development
===========

gravnoise uses Git for code management. The newest (and sometimes unstable) code
is available at::

  $ git clone git://gitorious.org/gravnoise/gravnoise.git


This document
=============

Copyright (C) 2012  Niels G. W. Serup

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and this
notice are preserved.  This file is offered as-is, without any warranty.
