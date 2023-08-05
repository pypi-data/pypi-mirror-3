

dumb is a suite of tools to manage collections of bookmarks that are:

* indipendent from the browser / application:
   dumb bookmarks can point to anything that has an URL, regardless 
   of the app needed to open them.
* shareable and distributed:
   dumb bookmarks are designed to be easily managed in a DVCS to provide 
   an easy mean to share a bookmark collection within a team, a community 
   or the whole world.

Getting dumb
------------

Homepage: http://dumb.grys.it
public git repository:

* `web interface <http://git.grys.it/?a=summary&p=dumb>`_
* git::

   git clone git://git.grys.it/dumb


Installation
------------

The dumb module depends on python >= 2.5 and `PyYAML <http://pyyaml.org/>`_.
Some scripts may require additional modules; e.g. dumb-to-jinja2 
requires `jinja2 <http://jinja.pocoo.org/>`_.
Support for python 3.x is planned, but still not implemented.

Dumb can be installed using distutils::

   python ./setup.py install


Documentation is in RestructuredText and can be built to various formats 
using `sphinx <http://sphinx.pocoo.org/>`_; in the ``docs/`` directory 
run e.g.:

   make html

to build the html documentation.
Manpages for the scripts are also available and can be build using::

   make man

