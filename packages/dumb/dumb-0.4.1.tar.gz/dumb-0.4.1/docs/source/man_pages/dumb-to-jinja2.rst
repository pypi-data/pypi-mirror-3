dumb-list
=========

SYNOPSIS
--------

   dumb-to-jinja2 [-v] [-k "<keyword1> [...]" ] -t <template> [collection]

DESCRIPTION
-----------

dumb-to-jinja2 passes a list of the bookmarks in a collection, 
possibly filtered by keyword, to the jinja2_ templating engine.

.. _jinja2: http://jinja.pocoo.org/

The template must be a valid jinja2 template and  can use a dict ``data`` 
which includes the collection url as specified in the command line in 
``data['collection']`` and the list of selected bookmarks in ``data['bms']``.

OPTIONS
-------

-h, --help
   Show an help message.
-k <keywords>, --keywords=<keywords> 
   Space separated keyword list.
-t <template>, --template=<template>
   Absolute path to a jinja2_ template.
-v, --verbose
   Be verbose.

SEE ALSO
--------

:doc:`dumb(1) <dumb>`

