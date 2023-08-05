### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

"""Log class for the Zope 3 based sterch.logfile package

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"


from datetime import datetime
from interfaces import ILog
import os, os.path
import time
from threading import Lock
from zope.interface import implements

class Log(object):
    """ Thread-safe system log. """
    implements(ILog)
       
    def __init__(self, logfile):
        self.lock = Lock()
        self.logfile = logfile
    
    def message(self, text):
        """Method that simply writes to log all information while posting"""
        self.lock.acquire()
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if os.path.isfile(self.logfile):
                f = open(self.logfile,'a')
            else:
                f = open(self.logfile,'w')
            f.write("%s %s\n" % (timestamp, text))
            f.close()
        except Exception, ex:
            self.lock.release()
            raise ex         
        self.lock.release()