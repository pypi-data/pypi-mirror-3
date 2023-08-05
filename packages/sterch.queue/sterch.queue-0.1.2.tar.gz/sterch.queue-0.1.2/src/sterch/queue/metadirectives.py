### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

"""ZCML directives interfaces for the ZTK based sterch.йгугу package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from zope.interface import Interface
from zope.schema import Int, TextLine

class IName(Interface):
    """ Utility name """
    name = TextLine(title=u"Name", required=False)
       
class IQueueDirective(IName):
    """ <queue .../> directive interface """
    maxsize = Int(title=u"Max number of items.",
                  description=u"Sets the upperbound limit on the number of items that can be placed in the queue.",
                  required=False,
                  min=0,
                  default=0)    
