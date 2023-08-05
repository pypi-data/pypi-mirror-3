### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for the <queue .../> directive 
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import sterch.queue
import Queue
import zope.app.component

from sterch.queue import interfaces
from StringIO import StringIO
from unittest import TestCase, makeSuite, main
from zope.component import queryUtility
from zope.component.testing import PlacelessSetup
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.xmlconfig import XMLConfig, xmlconfig 


class Test(PlacelessSetup, TestCase):
    """Test queue directive """
    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', sterch.queue)()
        XMLConfig('configure.zcml', sterch.queue)()

    def test_valid_zcml(self):
        xml=u"""<configure xmlns="http://namespaces.sterch.net/queue">
                    <queue />   
                    <queue name="My Queue"/>
                    <queue name="My Queue #2" maxsize="255"/>
                </configure>"""
        xmlconfig(StringIO(xml))
        self.assertTrue(queryUtility(interfaces.IQueue) is not None)
        self.assertTrue(queryUtility(interfaces.IQueue, name=u"My Queue") is not None)    
        self.assertTrue(queryUtility(interfaces.IQueue, name=u"My Queue #2") is not None)

    def test_invalid_zcml(self):
        xml=u"""<configure xmlns="http://namespaces.sterch.net/queue">
                    <queue name="Bad Queue" maxsize="-1"/>
                </configure>"""
        self.assertRaises(ConfigurationError, xmlconfig, StringIO(xml))
                   
def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')