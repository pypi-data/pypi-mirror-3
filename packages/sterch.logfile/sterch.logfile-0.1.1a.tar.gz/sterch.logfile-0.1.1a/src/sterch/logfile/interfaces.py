### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

"""Interfaces for the Zope 3 based sterch.logfile package

"""
__author__  = "Polscha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

from zope.interface import Interface
from zope.schema import Text, TextLine, Int
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('sterch.log')

class ILog(Interface):
    """ Inerface for filesystem log """
    
    def message(text):
        """ Writes message text to log """