from __future__ import absolute_import
from ..buml.baseWriterNodes import *
import unittest




#== Tests ========================================
class UtilityTests(unittest.TestCase):        
    "test baseWriterNodes"

#    def testNoseFindsMe(self):
#        "testNoseFindsMe: baseWriterNodes"
#        self.assertTrue(False)

    def testElementRendering(self):                    
        """various aspects of element rendering"""
        e = Element('div')
        self.assertEqual(e.singleAttStr('key', ['val']), 'key="val"')
        self.assertEqual(e.singleAttStr('key', ['v1', 'v2']), 'key="v1 v2"')
        #--
        e = Element('div')
        self.assertEqual(e.startTag(), '<div>')
        e.addAttr('class', 'cool')
        self.assertEqual(e.startTag(), '<div class="cool">')
        e.addAttr('class', 'wet')
        self.assertEqual(e.startTag(), '<div class="cool wet">')
        e.addAttr('id', 'z1')
        self.assertEqual(e.startTag(), '<div class="cool wet" id="z1">')


