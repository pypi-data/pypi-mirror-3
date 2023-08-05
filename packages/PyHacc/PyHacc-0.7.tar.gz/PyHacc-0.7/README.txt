Pre-requisites
--------------

You will need python (2.6 and 2.7 are tested), qtalchemy, sqlalchemy (0.7x 
preferred), a python database driver, and PyQt4 or PySide.  Refer to setup.py 
for a more complete list of dependencies.

It should be noted that while PyHacc is a fully functional system which is in
production use for the author's personal use, it is primarily a demonstration
and example of qtalchemy -- http://qtalchemy.org .

PyHacc can be run on both PyQt4 and PySide.  In the root of the mercurial 
repository, run the script qtbindings to switch between the two.  The source 
comes set up for PyQt4, but you can switch to PySide with::

    python qtbindings.py --platform=PySide
    python setup.py build
    sudo python setup.py install

If using PySide, the qtalchemy library will also need to be switched to 
using PySide in a similar way.


Getting Started
---------------

On linux, it should be sufficient to run::

    python setup.py build
    sudo python setup.py install
    pyhaccgui --conn=sqlite://

The sqlite:// connection string will start pyhacc with a demo database.

It is recommended and most tested to use pyhacc with postgresql.  To initialize 
a database::

    createdb pyhacc
    pyhacc initdb postgresql://username:password@localhost/pyhacc
    # to run pyhacc connected to this database:
    pyhaccgui --conn=postgresql://username:password@localhost/pyhacc

Getting Started on Windows
--------------------------

Roughly speaking, the install proceeds as follows:

- Install python and easy_install
- Install PyQt (or PySide, if desired).
- easy_install sqlalchemy
- easy_install pyscopg2  # for postgresql support
- easy_install pyhacc

On your postgresql server, run the following command::

    createdb pyhacc

Initialize the data-set with the following command on the windows client::

    c:\python27\python.exe c:\python27\scripts\pyhacc initdb postgresql://username:password@server/pyhacc

Create a windows short-cut with the following target for starting the program::

    c:\python27\pythonw.exe c:\python27\scripts\pyhaccgui --conn=postgresql://username:password@server/pyhacc

Changelog
---------

0.7:

* report changes with column width being propogated from on-screen lists to pdf
  versions
* factor out basic report code to qtalchemy
* bug fixes

0.6:  First pleasantly usable version in production

