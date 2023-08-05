### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

"""Metadirectives implementations for the ZTK based sterch.queue package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL" 

import interfaces
import Queue

from zope.component.zcml import handler

def queue(_context, maxsize=0, name=""):
    """ handler for <queue .../> directive """
    obj = Queue.Queue(maxsize)
    _context.action(
        discriminator = ('utility', interfaces.IQueue, name),
        callable = handler,
        args = ('registerUtility',
                obj, interfaces.IQueue, name)
        )