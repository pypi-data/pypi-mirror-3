#!/usr/bin/env python

""" 
pydumb

pydumb is a Python module to manage a dumb collection of bookmarks

"""

__author__ = 'Elena "of Valhalla" Grandi'
__version__ = '0.3.0'
__copyright__ = '2009-2011 Elena Grandi'
__license__ = 'LGPL'

import os,sys
import hashlib
import datetime
import logging

try:
    import yaml
except ImportError, ex:
    sys.stderr.write("This program requires the yaml module from http://pyyaml.org/\n")
    raise

# This class is available in the logging module from version 2.7
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class Collection:
    """"""

    def __init__(self,directory):
        """"""
        self.directory = directory
        self.bookmarks = {}
        self.keywords = []
        self.logger = logging.getLogger('dumb.Collection')
        self.logger.addHandler(NullHandler())

    def __contains__(self,bm_id):
        """"""
        return bm_id in self.bookmarks

    def __getitem__(self,bm_id):
        """Returns the bookmark with the given id/hash"""
        return self.bookmarks[bm_id]

    def fuzzy_get(self,partial_id):
        bms = []
        for bm_id in self.bookmarks:
            if bm_id.startswith(partial_id):
                bms.append(self.bookmarks[bm_id])
        return bms

    def load(self):
        """Reads the bookmarks in the collection directory"""
        for bfile in os.listdir(self.directory):
            bm = None
            try:
                fp = open(self.directory+'/'+bfile)
                bm = Bookmark(stream=fp)
            except IOError:
                self.logger.info(bfile+" is not a readable file")
            except ValueError:
                self.logger.info(bfile+" is not a bookmark file")
            if bm != None:
                self.bookmarks[bm.bm_id] = bm
                if 'keywords' in bm:
                    for keyword in bm['keywords']:
                        if keyword not in self.keywords:
                            self.keywords.append(keyword)

    def save(self):
        """Saves the current bookmarks"""
        for bm_id in self.bookmarks:
            bm = self.bookmarks[bm_id]
            filename = os.path.join(self.directory,bm_id)
            try:
                fp = open(filename,'w')
            except IOError:
                self.logger.error("Could not open file "+filename+" for writing")
                raise
            try: 
                bm.dump(fp)
            except IOError:
                self.logger.error("Could not write to "+filename)
                raise
            finally:
                fp.close()

    def add_bookmark(self,data):
        """Adds a new bookmark to the collection from a dict of data"""

        try:
            bm = Bookmark(data=data)
            self.bookmarks[bm.bm_id] = bm
        except KeyError:
            raise ValueError, "A bookmark must have an url"
        if 'keywords' in data:
            for keyword in data['keywords']:
                if keyword not in self.keywords:
                    self.keywords.append(keyword)


    def get_bookmarks(self,keywords=None):
        """Returns a list of the bookmarks with the given tags.
        If kkeywords == None, return every bookmark in the collection."""
        if keywords == None:
            return self.bookmarks.values()
        bms = []
        if type(keywords) == list:
            for bm in self.bookmarks:
                for keyword in keywords:
                    if 'keywords' in self.bookmarks[bm] and keyword in self.bookmarks[bm]['keywords']:
                        bms.append(self.bookmarks[bm])
                        break
        return bms

    def get_base_bookmarks(self,url):
        bms = []
        for bm in self.bookmarks:
            if self.bookmarks[bm]['url'] in url:
                bms.append(self.bookmarks[bm])
        return bms

    def get_keywords(self):
        """Returns the list of keywords in this collection"""
        return self.keywords

    def get_short_id(self,bm_id):
        """Return a minimal substring that identifies a bookmark"""
        bms = self.fuzzy_get(bm_id[:4])
        if len(bms) == 0:
            return None
        elif len(bms) == 1:
            return bm_id[:4]
        elif len(self.fuzzy_get(bm_id[:8])) == 1:
            return bm_id[:8]
        elif len(self.fuzzy_get(bm_id[:12])) == 1:
            return bm_id[:12]
        elif len(self.fuzzy_get(bm_id[:16])) == 1:
            return bm_id[:16]
        elif len(self.fuzzy_get(bm_id[:20])) == 1:
            return bm_id[:20]
        elif len(self.fuzzy_get(bm_id[:24])) == 1:
            return bm_id[:24]
        elif len(self.fuzzy_get(bm_id[:28])) == 1:
            return bm_id[:28]
        else:
            return bm_id


class Bookmark():
    """"""

    def __init__(self,data=None,stream=None):
        """Creates a new bookmark instance.
        """

        self.logger = logging.getLogger('dumb.Bookmark')
        self.logger.addHandler(NullHandler())
        self.data = {}
        if data != None:
            try:
                self.data['url'] = unicode(data['url'])
            except KeyError:
                raise ValueError, "Could not find an url in the given data"
            self.bm_id = hashlib.md5(self.data['url']).hexdigest()
            self.load_data(data)
        elif stream != None:
            try:
                parsed_data = yaml.safe_load(stream)
            except yaml.YAMLError:
                raise ValueError, "Could not find sane yaml data in the given stream"
            if not 'url' in parsed_data:
                raise ValueError, "Could not find an url in the given data"
            self.load_data(parsed_data)
            self.bm_id = hashlib.md5(self.data['url']).hexdigest()
        else:
            raise ValueError, "a Bookmark must be initialized with either a data dict or a yaml stream"

    def __str__(self):
        """"""
        return yaml.safe_dump(self.data,default_flow_style=False)

    def __repr__(self):
        """"""
        return repr(self.data)

    def __getitem__(self,key):
        """"""
        return self.data[key]

    def __setitem__(self,key,value):
        """"""
        self.load_data({key: value})

    def __contains__(self,key):
        """"""
        return self.data.has_key(key)

    #def get_parsed_value(self,key):
    #    """Returns the value of the given key with %(url)s explicited"""
    #    return self.data[key].replace("%(url)s",self.data['url'])

    def dump(self,stream):
        """Dumps a yaml representation of itself as utf8 encoded text"""

        yaml.safe_dump(self.data,stream,default_flow_style=False,encoding='utf8')

    def load_data(self,data):
        """Loads the bookmark informations from a dict"""
        # url: mandatory
        try:
            self.data['url'] = unicode(data['url'])
        except TypeError:
            raise TypeError, "Could not convert url to unicode"
        except KeyError:
            pass
        # keys with a single, (unicode) string value
        for key in ['title','comment','content-type','cline']:
            try:
                self.data[key] = unicode(data[key])
            except (TypeError,KeyError):
                pass
        # keys with datetime value
        for key in ['added','last-seen']:
            try:
                if type(data[key]) == datetime.datetime:
                    self.data[key] = data[key]
            except KeyError:
                pass
        # keywords: sequence of strings
        if data.has_key('keywords'):
            if not self.data.has_key('keywords'):
                self.data['keywords'] = []
            for keyword in data['keywords']:
                try:
                    self.data['keywords'].append(unicode(keyword))
                except ValueError:
                    pass
        # mirrors: dicts with string values for url and server and 
        # datetime added
        if data.has_key('mirrors'):
            if not self.data.has_key('mirrors'):
                self.data['mirrors'] = []
            for mirror in data['mirrors']:
                mdata = {}
                for key in ['url','server']:
                    try:
                        mdata[key] = unicode(mirror[key])
                    except (TypeError, KeyError):
                        pass
                try:
                    if type(mirror['added']) == datetime.datetime:
                        mdata['added'] = mirror['added']
                except KeyError:
                    pass
                self.data['mirrors'].append(mdata)
        # positions: dicts with string values for url, title and comment 
        # and datetime added
        if data.has_key('positions'):
            if not self.data.has_key('positions'):
                self.data['positions'] = []
            for pos in data['positions']:
                pdata = {}
                for key in ['url','title','comment']:
                    try:
                        pdata[key] = unicode(pos[key])
                    except (TypeError, KeyError):
                        pass
                try:
                    if type(pos['added']) == datetime.datetime:
                        pdata['added'] = pos['added']
                except KeyError:
                    pass
                self.data['positions'].append(pdata)
        # related: dicts with string values for url, title, comment 
        # and relation, and datetime added
        if data.has_key('related'):
            if not self.data.has_key('related'):
                self.data['related'] = []
            for rel in data['related']:
                rdata = {}
                for key in ['url','title','comment','relation']:
                    try:
                        rdata[key] = unicode(rel[key])
                    except (TypeError, KeyError):
                        pass
                try:
                    if type(rel['added']) == datetime.datetime:
                        rdata['added'] = rel['added']
                except KeyError:
                    pass
                self.data['related'].append(rdata)


def main():
    pass


if __name__ == '__main__': main()
