dumb-add
========

SYNOPSIS
--------

   dumb-add [-v] [-t <Title>] [-l <Command-line>] [-c <Comment>] [-o <opener>] [-k "<keyword1> [...]"] url [collection]

DESCRIPTION
-----------

dumb-add creates a dumb bookmark with the given values.

An existing bookmark with exactly the same url will be silently overwritten.

OPTIONS
-------

-v, --verbose
   Be verbose.
-t <title>, --title=<title>                             
   Document title.
-l <command-line>, --command-line=<command-line>
   A command line that can open the url.
-c <comment>, --comment=<comment>
   Freeform text comment.
-o <opener>, --opener=<opener>
   A category of program that can open the url such as browser.
-k <keywords>, --keywords=<keywords> 
   Space separated keyword list.


SEE ALSO
--------

:doc:`dumb(1) <dumb>`

