Bookmark File Format
====================

dumb bookmarks are YAML_ documents with a sequence of 
mappings indexed by the keys described below.

A dumb collection stores such bookmarks in a directory, using a file 
for each bookmark, named with an md5 hash of its url.

Bookmark fields
---------------

``url``: (URL)
   this is the main URL pointed to by the bookmark, must be unique in 
   the collection.

``title``: (string)
   title of the bookmark; often taken from the ``title`` tag of HTML documents.

``comment``: (string)
   freeform comment.

``content-type``: (string)
   Content-Type / Internet Media Type of the pointed resource.

``added``: (datetime)
   Date when the bookmark was first added.

``last-seen``: (datetime)
   Date when the pointed resource was last seen and confirmed to 
   be of interest.

``cline``: (string)
   A command line that can open the pointed resource.
   Clients are encouraged to prevent direct execution of this line 
   from untrusted sources.

``keywords``: (sequence of strings)
   A list of keywords/tags to categorize the bookmark.

``mirrors``: (sequence of mappings with the keywords ``url`` ``added`` and ``server``)
   A list of available mirrors for the resource, where ``server`` is a string 
   that identifies the server.

``positions``: (sequence of mappings with the keywords ``url``, ``added``, ``title``, and ``comment``)
   A list of subbookmars in the original resource; e.g. pages 
   in a website or line numbers in a text file.

``related``: (sequence of mappings with the keywords ``url``, ``added``, ``title``, ``comment`` and ``relation``)
  A list of related resources, e.g. the parent 

.. _YAML: http://www.yaml.org
