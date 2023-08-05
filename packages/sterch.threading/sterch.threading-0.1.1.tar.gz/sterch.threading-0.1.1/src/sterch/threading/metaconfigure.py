### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2008
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2008
#######################################################################

"""Metadirectives implementations for the ZTK based sterch.threading package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL" 

import interfaces
import threading

from zope.component.zcml import handler

def thread(_context, target, name=""):
    """ handler for <thread .../> directive """
    obj = threading.Thread(target=target)
    _context.action(
        discriminator = ('utility', interfaces.IThread, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.IThread, name)
        )
    
def lock(_context, name=""):
    """ handler for <lock .../> directive """
    obj = threading.Lock()
    _context.action(
        discriminator = ('utility', interfaces.ILock, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.ILock, name)
        )
    
def rlock(_context, name=""):
    """ handler for <rlock .../> directive """
    obj = threading.RLock()
    _context.action(
        discriminator = ('utility', interfaces.IRLock, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.IRLock, name)
        )
    
def condition(_context, lock=None, name=""):
    """ handler for <condition .../> directive """

    obj = threading.Condition()
    _context.action(
        discriminator = ('utility', interfaces.ICondition, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.ICondition, name)
        )
    
def semaphore(_context, value=1, name=""):
    """ handler for <semaphore .../> directive """

    obj = threading.Semaphore(value)
    _context.action(
        discriminator = ('utility', interfaces.ISemaphore, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.ISemaphore, name)
        )
    
def event(_context, name=""):
    """ handler for <event .../> directive """

    obj = threading.Event()
    _context.action(
        discriminator = ('utility', interfaces.IEvent, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.IEvent, name)
        )

def timer(_context, interval, function, name=""):
    """ handler for <timer .../> directive """

    obj = threading.Timer(interval, function)
    _context.action(
        discriminator = ('utility', interfaces.ITimer, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.ITimer, name)
        )