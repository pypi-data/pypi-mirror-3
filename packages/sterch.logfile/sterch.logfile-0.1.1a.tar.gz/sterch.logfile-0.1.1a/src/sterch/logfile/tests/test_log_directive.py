### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for the <log .../> directive 
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import os
import sterch.logfile
import tempfile
import zope.component

from sterch.logfile import interfaces
from StringIO import StringIO
from unittest import TestCase, makeSuite, main
from zope.component import queryUtility
from zope.component.testing import PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig, xmlconfig 

class Test(PlacelessSetup, TestCase):
    """Test queue directive """
    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.component)()
        XMLConfig('meta.zcml', sterch.logfile)()
        XMLConfig('configure.zcml', sterch.logfile)()
        self.logfile1 = tempfile.mktemp()
        self.logfile2 = tempfile.mktemp()
        

    def test_log(self):
        xml=u"""<configure xmlns="http://namespaces.sterch.net/logfile">
                    <log name="error" path="%s"/>
                    <log path="%s"/>                
                </configure>""" % (self.logfile1, self.logfile2)
        xmlconfig(StringIO(xml))
        log1 = queryUtility(interfaces.ILog)
        log2 = queryUtility(interfaces.ILog, name="error")
        self.assertTrue(log1 is not None)
        self.assertTrue(log2 is not None)
        msg = "Test message"
        log1.message(msg)
        log2.message(msg)
        text = open(self.logfile1,"r").read()
        self.assertTrue(msg in text)
        text = open(self.logfile2,"r").read()
        self.assertTrue(msg in text)
    
    def tearDown(self):
        os.remove(self.logfile1)
        os.remove(self.logfile2)
        super(Test,self).tearDown()
                   
def test_suite():
    suite = makeSuite(Test)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')