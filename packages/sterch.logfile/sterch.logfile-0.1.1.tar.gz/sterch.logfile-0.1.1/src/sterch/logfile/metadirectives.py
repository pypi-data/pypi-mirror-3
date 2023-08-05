### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

"""ZCML directives interfaces for the Zope 3 based sterch.logfile package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from zope.interface import Interface
from zope.configuration.fields import Path
from zope.schema import TextLine

class ILogDirective(Interface):
    """ <log .../> directive interface """
    name = TextLine(title=u"Log name", required=False)
    
    path = Path(title=u"Path",
            description=u"Path to logfile",              
            required=True)