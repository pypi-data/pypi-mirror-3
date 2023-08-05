### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

"""Metadirectives implementation class for the Zope 3 based sterch.logfile package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from interfaces import ILog 
from log import Log
from zope.component.zcml import handler

def log(_context, path, name=""):
    """ handler for the <log .../> directive """
    l = Log(path)
    _context.action(
        discriminator = ('utility', ILog, name),
        callable = handler,
        args = ('registerUtility',
                l, ILog, name)
        )