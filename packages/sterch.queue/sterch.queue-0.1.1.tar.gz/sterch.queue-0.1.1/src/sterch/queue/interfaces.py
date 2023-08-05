### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################
"""Interfaces for the Zope 3 based sterch.queue package

$Id: interfaces.py 16665 2010-12-03 14:07:39Z maxp $
"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL" 

from zope.interface.common.interfaces import IException  
from zope.interface import Interface
from zope.schema import TextLine, Int, Bool
       
class IQueueException(IException):
    """ Common Queue exception """
    
class IFullException(IQueueException):
    """ Queue is full """

class IEmptyException(IQueueException):
    """ Queue is empty """

class IQueue(Interface):
    """ A synchronized queue """
    def qsize():
        """ Return the approximate size of the queue. Note, qsize() > 0 doesn’t guarantee that a subsequent get() will not block, nor will qsize() < maxsize guarantee that put() will not block."""     
    
    def empty():
        """ Return True if the queue is empty, False otherwise. If empty() returns True it doesn’t guarantee that a subsequent call to put() will not block. Similarly, if empty() returns False it doesn’t guarantee that a subsequent call to get() will not block."""
    
    def full():
        """ Return True if the queue is full, False otherwise. If full() returns True it doesn’t guarantee that a subsequent call to get() will not block. Similarly, if full() returns False it doesn’t guarantee that a subsequent call to put() will not block."""
    
    def put(item, block=True, timeout=None):
        """ Put item into the queue. If optional args block is true and timeout is None (the default), block if necessary until a free slot is available. If timeout is a positive number, it blocks at most timeout seconds and raises the Full exception if no free slot was available within that time. Otherwise (block is false), put an item on the queue if a free slot is immediately available, else raise the Full exception (timeout is ignored in that case)."""

    def put_nowait(item):
        """ Equivalent to put(item, False) """
    
    def get(block=True, timeout=None):
        """ Remove and return an item from the queue. If optional args block is true and timeout is None (the default), block if necessary until an item is available. If timeout is a positive number, it blocks at most timeout seconds and raises the Empty exception if no item was available within that time. Otherwise (block is false), return an item if one is immediately available, else raise the Empty exception (timeout is ignored in that case)."""

    def get_nowait():
        """ Equivalent to get(False)."""
        
    def task_done():
        """ Indicate that a formerly enqueued task is complete. Used by queue consumer threads. For each get() used to fetch a task, a subsequent call to task_done() tells the queue that the processing on the task is complete."""

    def join():
        """ Blocks until all items in the queue have been gotten and processed."""