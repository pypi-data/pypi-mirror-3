### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for sterch.Queue mobule objects and classes 
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import sterch.queue
import Queue
import zope.app.component

from sterch.queue import interfaces
from unittest import TestCase, makeSuite, main
from zope.component.testing import PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig 


class Test(PlacelessSetup, TestCase):
    """Test queue classes and objects """
    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('configure.zcml', sterch.queue)()

    def testClasses(self):
        self.assertTrue(interfaces.IQueue.implementedBy(Queue.Queue))
        self.assertTrue(interfaces.IEmptyException.implementedBy(Queue.Empty))
        self.assertTrue(interfaces.IFullException.implementedBy(Queue.Full))
    
    def test_objects(self):
        self.assertTrue(interfaces.IQueue.providedBy(Queue.Queue()))
        self.assertTrue(interfaces.IEmptyException.providedBy(Queue.Empty()))
        self.assertTrue(interfaces.IFullException.providedBy(Queue.Full()))
                   
def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
