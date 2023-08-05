### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for the <lock .../> <rlock .../> directive 
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
                    <lock />
                    <lock name="My Lock"/>
                    <rlock />
                    <rlock name="My RLock"/>                   
                </configure>"""
        xmlconfig(StringIO(xml))
        self.assertTrue(queryUtility(interfaces.ILock) is not None)
        self.assertTrue(queryUtility(interfaces.ILock, name=u"My Lock") is not None)
        self.assertTrue(queryUtility(interfaces.IRLock) is not None)
        self.assertTrue(queryUtility(interfaces.IRLock, name=u"My RLock") is not None)
    
                   
def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
