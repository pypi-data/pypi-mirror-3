### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################
"""Interfaces for the ZTK based sterch.threading package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL" 

from zope.interface import Interface
from zope.schema import TextLine, Int, Bool

class IThread(Interface):
    """ Interface of python thread """
    
    name = TextLine(title = u"Thread name",
                    description = u"A string used for identification purposes only. It has no semantics.",
                    )

    def __init__(group=None, target=None, name=None, args=(), kwargs={}):
        """ Constructor """
    
    def start():
        """ Start the thread’s activity. """
        
    def run():
        """ Method representing the thread’s activity. """
        
    def join(timeout=None):
        """ Wait until the thread terminates. """
        
    def isAlive():
        """ Return whether the thread is alive. """
    
    is_alive = isAlive
    
    daemon = Bool(title = u"Is daemon thread",
                  description = u"A boolean value indicating whether this thread is a daemon thread (True) or not (False).")

class ILock(Interface):
     """ Interface of lock """
     def acquire(blocking=1):
         """ Acquire a lock, blocking or non-blocking. """
         
     def release():
         """ Release a lock. """
         
class IRLock(ILock):
    """ A reentrant lock is a synchronization primitive 
        that may be acquired multiple times by the same thread. """
        
        
class ICondition(Interface):
    """ A condition variable is always associated with some kind of lock 
        this can be passed in or one will be created by default. """ 
    
    def __init__(lock=None):
        """ If the lock argument is given and not None, 
            it must be a Lock or RLock object, and it is used as the underlying lock. 
        """
        
    def acquire(*args):
        """ Acquire the underlying lock. """
    
    def release():
        """ Release the underlying lock. """    
    
    def wait(timeout=None):
        """ Wait until notified or until a timeout occurs. """
    
    def notify():
        """ Wake up a thread waiting on this condition. """
    
    def notifyAll():
        """ Wake up all threads waiting on this condition."""
    
    notify_all = notifyAll
               
class ISemaphore(ILock):
    """ A semaphore manages an internal 
        counter which is decremented by each acquire() 
        call and incremented by each release() call."""

    def __init__(value=1):
        """ The optional argument gives the initial value for the internal counter. """
        
class IEvent(Interface):
    """ This is one of the simplest mechanisms for communication between threads """
    
    def isSet():
        """ Return true if and only if the internal flag is true."""
    
    is_set = isSet
    
    def set():
        """ Set the internal flag to true. """
    
    def clear():
        """ Reset the internal flag to false. """
        
    def wait(timeout=None):
        """ Block until the internal flag is true. """
        
class ITimer(Interface):
    """ This class represents an action that 
        should be run only after a certain amount of time has passed — a timer. """
        
    def __init__(interval, function, args=[], kwargs={}):
        """ Create a timer that will run function with arguments args and keyword 
            arguments kwargs, after interval seconds have passed. """
    
    def start():
        """ Start the timer. """
    
    def cancel():
        """ Stop the timer, and cancel the execution of the timer’s action."""