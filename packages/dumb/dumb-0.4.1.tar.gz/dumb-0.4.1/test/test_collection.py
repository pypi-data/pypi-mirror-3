#!/usr/bin/env python

import dumb
import unittest
import tempfile, os, shutil, hashlib
import yaml

class TestCollection(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.cl = dumb.Collection(self.directory)

    def tearDown(self):
        shutil.rmtree(self.directory)

    def testAddBookmark(self):
        data={'url':'http://www.example.com',
                'title':'An example website'}
        self.cl.add_bookmark(data)
        url_hash = hashlib.md5('http://www.example.com').hexdigest()
        self.assertTrue(url_hash in self.cl)
        self.assertEqual(self.cl[url_hash]['url'],'http://www.example.com')

    def testAddBookmarkWithKeywords(self):
        data={'url':'http://www.example.com',
                'title':'An example website',
                'keywords':['example','test']}
        self.cl.add_bookmark(data)
        self.assertTrue('test' in self.cl.keywords)
        self.assertTrue('example' in self.cl.keywords)

    def testGetBaseBookmarks(self):
        self.cl.add_bookmark({'url':'http://www.example.com',
            'title':'An example website'})
        self.cl.add_bookmark({'url':'http://www.example.org',
            'title':'An example organization'})
        url_hash = hashlib.md5('http://www.example.org').hexdigest()
        bm_i_want = [ self.cl[url_hash] ]
        bm_i_get = self.cl.get_base_bookmarks('http://www.example.org/page_1')
        self.assertEqual(bm_i_want,bm_i_get)

    def testGetMultipleBaseBookmarks(self):
        self.cl.add_bookmark({'url':'http://www.example.com',
            'title':'An example website'})
        self.cl.add_bookmark({'url':'http://www.example.org',
            'title':'An example organization'})
        self.cl.add_bookmark({'url':'http://www.example.org/section_1',
            'title':'An example organization'})
        url_hash_1 = hashlib.md5('http://www.example.org').hexdigest()
        url_hash_2 = hashlib.md5('http://www.example.org/section_1').hexdigest()
        bm_i_want = [ self.cl[url_hash_1], self.cl[url_hash_2] ]
        bm_i_get = self.cl.get_base_bookmarks('http://www.example.org/section_1/page_42')
        for bm in bm_i_want:
            self.assertTrue(bm in bm_i_get)
        self.assertEqual(len(bm_i_want),len(bm_i_get))

    def testGetBookmarkFromPartialURL(self):
        self.cl.add_bookmark({'url':'http://www.example.com',
            'title':'An example website'})
        self.cl.add_bookmark({'url':'http://www.example.org',
            'title':'An example organization'})
        url_hash = hashlib.md5('http://www.example.org').hexdigest()
        bm_i_want = [ self.cl[url_hash] ]
        bm_i_get = self.cl.fuzzy_get(url_hash[:3])
        self.assertEqual(bm_i_want,bm_i_get)


class TestCollectionFiles(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.directory = self.tempdir+"/dumb"
        shutil.copytree('test/example_data',self.directory)
        self.cl = dumb.Collection(self.directory)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def testLoadCollection(self):
        self.cl.load()
        url_hash = hashlib.md5('http://example.com').hexdigest()
        self.assertTrue(url_hash in self.cl)
        self.assertTrue('example' in self.cl.keywords)

    def testSaveCollection(self):
        data = {'url':"http://www.example.it"}
        self.cl.add_bookmark(data)
        self.cl.save()
        self.assertTrue(os.path.exists(self.directory+'/eeff1b54986e9e9aaa1ee53e1105d0c8'))
        fp = open(self.directory+'/eeff1b54986e9e9aaa1ee53e1105d0c8','r')
        self.assertTrue("http://www.example.it" in fp.read())
        fp.close()



if __name__ == '__main__':
    unittest.main()
