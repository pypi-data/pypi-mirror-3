#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2 as unittest
import nodetree

class NodeTreeTest(unittest.TestCase):
    def setUp(self):
        self.d1 = nodetree.Document()
        self.d2 = nodetree.Document()

    def tearDown(self):
        pass
        
    def test_root_element(self):
        '''
        Test setting an element to root element of two documents.
        '''
        e = nodetree.Element('foo')
        self.d1.root = e
        self.d2.root = e
        
        expected = \
'''<?xml version="1.0"?>
<foo/>
'''
        self.assertEqual(str(self.d1), expected)
        self.assertEqual(str(self.d2), expected)

    def test_attribute(self):
        '''
        Test setting an attribute to an element.
        '''
        e = nodetree.Element('foo')
        self.d1.root = e
        self.d2.root = e

        e.attributes['bar'] = '1'

        expected = \
'''<?xml version="1.0"?>
<foo bar="1"/>
'''
        self.assertEqual(str(self.d1), expected)
        self.assertEqual(str(self.d2), expected)

    def  test_name(self):
        '''
        Test changing element name.
        '''
        e = nodetree.Element('foo')
        self.d1.root = e
        self.d2.root = e

        e.name = 'bar'

        expected = \
'''<?xml version="1.0"?>
<bar/>
'''
        self.assertEqual(str(self.d1), expected)
        self.assertEqual(str(self.d2), expected)   

if __name__ == '__main__':
    unittest.main()
