#!/usr/bin/env python

import dumb
import unittest
import tempfile, os
import yaml

class TestBookmark(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testsetBMKey(self):
        bm=dumb.Bookmark(data={'url':'http://www.example.com'})
        bm['title']='An example'
        self.assertEqual(bm['title'],'An example')

    def testsetBMWrongKey(self):
        bm=dumb.Bookmark(data={'url':'http://www.example.com'})
        bm['not a key']="Not a value"
        self.assertFalse('not a key' in bm)


class TestBookmarkCreation(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testcreateSimpleBMfromYAML(self):
        yaml_string = """
url: "http://example.com"
title: "An example bookmark"
        """
        bm = dumb.Bookmark(stream=yaml_string)
        self.assertEqual(bm['url'],"http://example.com")
        self.assertEqual(bm['title'],'An example bookmark')

    def testcreateSimpleBMfromData(self):
        data = {'url':"http://example.com",'title':"An example bookmark"}
        bm = dumb.Bookmark(data=data)
        self.assertEqual(bm['url'],u"http://example.com")
        self.assertEqual(bm['title'],u'An example bookmark')

    def testcreateFullBMfromYAML(self):
        fp = open('test/example_data/a9b9f04336ce0181a08e774e01113b31','r')
        bm = dumb.Bookmark(stream=fp)
        fp.close()
        fp = open('test/example_data/a9b9f04336ce0181a08e774e01113b31','r')
        data = yaml.safe_load(fp)
        fp.close()
        # I test that every key has been loaded, and hope that 
        # the yaml module did load the right thing
        for key in data:
            self.assertTrue(key in bm)

    def testcreateBMfromBadData(self):
        data = {'url':"http://example.com",'not a key':"Not a value"}
        bm = dumb.Bookmark(data=data)
        self.assertFalse('not a key' in bm)

    def testcreateBMfromBadYAML(self):
        yaml_string = """
url: "http://example.com"
notakey: "Not a value"
        """
        bm = dumb.Bookmark(stream=yaml_string)
        self.assertFalse('notakey' in bm)






if __name__ == '__main__':
    unittest.main()
