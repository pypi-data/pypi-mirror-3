PubliForge README
=================

Installation and Setup
----------------------

Install ``PubliForge`` (best practice is to do so in a virtual environment)::

    $ cd <directory_containing_this_file>
    $ python setup.py develop

Tweak the configuration file ``development.ini`` as appropriate and populate
database::

    $ pfpopulate development.ini    

Getting Started
---------------

Launch the apllication::

    $ pserve --reload development.ini

And, visit http://localhost:6543.

Documentation
-------------

Read documentation (http://doc.publiforge.org) for complete information.

$Id: README.txt 0875d8dc7fd1 2011/12/31 18:06:04 patrick $
