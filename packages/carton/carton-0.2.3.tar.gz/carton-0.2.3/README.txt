carton
======

make a self-extracting virtualenv from directories or URLs of packages

See the docstring of carton.py for documentation: http://k0s.org/mozilla/hg/carton/file/tip/carton.py#l3

Carton provides a one-file portable package of a virtualenv and all of
its software.

Carton lives at http://k0s.org/mozilla/hg/carton

Tests illustrating carton's use are at
http://k0s.org/mozilla/hg/carton/file/tip/tests/doctest.txt

A self-extracting carton of, um, carton is at 
http://k0s.org/mozilla/hg/carton/file/tip/carton-env.py


Why did you write this thing?
-----------------------------

For whatever reasons, people have trouble using virtualenv so I
figured I'd make that easy.  People also seem to believe that you can
zip up a virtualenv and treat it as portable.  In general, virtualenvs
are architecture and library dependent, so this isn't a good idea.
carton works around this problem by packaging the instructions
necessary to make the virtualenv instead of dealing with
library/hardware incompatabilities.


Should I use carton for my deployment strategy?
-----------------------------------------------

Maybe.  Carton is pretty minimalist.  It does effectively one thing:
makes a file that unfolds to a virtualenv with software setup for
development.  If this fits in with what you want to do, then sure!  If
not, then probably not.


TODO
----

carton is essentially finished.  Features can be added by request
(just mail me: jhammel __at__ mozilla __dot__ com), but the scope of
the project is pretty much fulfilled.

There are a few items I would like to add:

- currently, carton only works if connected to a network or if a local
  virtualenv tarball is specified with `--virtualenv`. I would like to
  make a script, `regen_virtualenv.py`, that would add a hashed value
  of the virtualenv tarball to the global `VIRTUAL_ENV`
  variable. Similarly, one should be able to retrieve the stripped
  down version of the script without this hash if desired

- ... and being able to take virtualenv from its import path, if
  available

- it would be nice to be able to specify a post-deployment script to
  be run 


Links
-----

Projects solving related problems:

* https://github.com/jbalogh/vending-machine: a script for managing
  vendor libraries
  

* https://bitbucket.org/kumar303/eco: Eco helps you maintain a local
  Python ecosystem

* https://bitbucket.org/kumar303/velcro/: Velcro is a script that sets
  up a Python project for local installation. Essentially, it
  "fastens" together virtualenv and optionally pip too.

* http://www.virtualenv.org/en/latest/index.html#creating-your-own-bootstrap-scripts
