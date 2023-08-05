### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

"""ZCML directives interfaces for the ZTK based sterch.threading package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from interfaces import ILock
from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.schema import TextLine, Int, Float

class IName(Interface):
    """ Utility name """
    name = TextLine(title=u"Name", required=False)
       
class ILockDirective(IName):
    """ <lock .../> directive interface """
    
class IRLockDirective(IName):
    """ <rlock .../> directive interface """

class IThreadDirective(IName):
    """ <thread .../> directive interface """
    
    target = GlobalObject(title=u"Callable object (i.e. function, object, class)", 
                          required=True)

class IConditionDirective(IName):
    """ <condition .../> directive interface """
    lock = GlobalObject(title=u"Lock object to use.",
                    description=u"If the lock argument is given and not None, it must be a object that implements ILock is used as the underlying lock. Otherwise, a new RLock object is created and used as the underlying lock.", 
                    required=False)
    
class ISemaphoreDirective(IName):
    """ <semaphore .../> directive interface """
    value = Int(title=u"Initial value for the internal counter.",
                description=u"Defaults to 1. Must be positive or zero.",
                required=False,
                min=0,
                default=1)

class IEventDirective(IName):
    """ <event .../> directive interface """
    
class ITimerDirective(IName):
    """ <timer .../> directive interface """
    interval = Float(title=u"Interval (in sec.) before its action has begun.", min=0.0, required=True)
    function = GlobalObject(title=u"Callable object (i.e. function, object, class)", 
                            required=True)