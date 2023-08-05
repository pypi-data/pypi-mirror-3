### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for standard threading mobule objects and classes 
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import sterch.threading
import threading
import zope.app.component

from sterch.threading import interfaces
from unittest import TestCase, makeSuite, main
from zope.component.testing import PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig 


class Test(PlacelessSetup, TestCase):
    """Test threading classes and objects """
    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('configure.zcml', sterch.threading)()

    def testClasses(self):
        self.assertTrue(interfaces.IThread.implementedBy(threading.Thread))
        self.assertTrue(interfaces.ILock.implementedBy(threading._RLock))
        self.assertTrue(interfaces.ICondition.implementedBy(threading._Condition))
        self.assertTrue(interfaces.ISemaphore.implementedBy(threading._Semaphore))
        self.assertTrue(interfaces.IEvent.implementedBy(threading._Event))
        self.assertTrue(interfaces.ITimer.implementedBy(threading._Timer))
    
    def test_objects(self):
        self.assertTrue(interfaces.IThread.providedBy(threading.Thread()))
        self.assertTrue(interfaces.ILock.providedBy(threading.RLock()))
        self.assertTrue(interfaces.IRLock.providedBy(threading.RLock()))
        self.assertTrue(interfaces.ICondition.providedBy(threading.Condition()))
        self.assertTrue(interfaces.IEvent.providedBy(threading.Event()))
        self.assertTrue(interfaces.ITimer.providedBy(threading.Timer(0.01, lambda:0)))
                   
def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
