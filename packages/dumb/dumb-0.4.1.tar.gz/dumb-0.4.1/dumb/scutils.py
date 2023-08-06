
""" 
scutils - Script Utils

This module provides some helper functions to dumb scripts.

- get_bm_listing - returns a compact listing of bookmarks
"""

__author__ = 'Elena "of Valhalla" Grandi'
__version__ = '0.4.0'
__copyright__ = '2009-2011 Elena Grandi'
__license__ = 'LGPL'

import os

import dumb

def get_bm_listing(bookmarks,collection,short=False):
    """Return a listing of bookmarks as a string.

    format is::

        short_id: title \\n      <url>\\n

    or, if short=True::

        short_id: title <url>\\n

    """
    s = ""
    for bm in bookmarks:
        s_id = collection.get_short_id(bm.bm_id)
        if s_id != None:
            try:
                title = bm['title']
            except KeyError:
                title = ""
            url = '<' + bm['url'] + '>'
            if short:
                sep = ' '
            else:
                sep = '\n      '
            s += (s_id + ': ' + title + sep + url + '\n')
    return s

def create_bookmark(data,directory):
    """Creates and saves a bookmark with given data in a directory

    Raise 
    - ValueError: if the Bookmark can't be created with the data;
    - IOError: if there had been probles writing to the file"""

    bm=dumb.Bookmark(data)
    filename = os.path.join(directory,bm.bm_id)
    fp = open(filename,'w')
    try:
        bm.dump(fp)
    finally:
        fp.close()

    return filename


