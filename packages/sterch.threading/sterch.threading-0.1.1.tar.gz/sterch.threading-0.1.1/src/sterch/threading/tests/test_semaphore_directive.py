### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for the <semaphore .../> directive 
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import sterch.threading
import threading
import zope.app.component

from sterch.threading import interfaces
from StringIO import StringIO
from unittest import TestCase, makeSuite, main
from zope.component import queryUtility
from zope.component.testing import PlacelessSetup
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.xmlconfig import XMLConfig, xmlconfig 

class Test(PlacelessSetup, TestCase):
    """Test threading classes and objects """
    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', sterch.threading)()
        XMLConfig('configure.zcml', sterch.threading)()

    def test_valid_zcml(self):
        xml=u"""<configure xmlns="http://namespaces.sterch.net/threading">
                    <semaphore />
                    <semaphore name="My Semaphore" value="2"/>
                </configure>"""
        xmlconfig(StringIO(xml))
        self.assertTrue(queryUtility(interfaces.ISemaphore) is not None)
        self.assertTrue(queryUtility(interfaces.ISemaphore, name=u"My Semaphore") is not None)
        
    def test_invalid_zcml(self):
        xml=u"""<configure xmlns="http://namespaces.sterch.net/threading">
                    <semaphore name="My Semaphore" value="-1"/>
                </configure>"""
        self.assertRaises(ConfigurationError, xmlconfig, StringIO(xml))
                   
def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
