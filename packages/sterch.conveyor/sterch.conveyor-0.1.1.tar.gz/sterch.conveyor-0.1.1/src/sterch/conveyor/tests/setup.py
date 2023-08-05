### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Base test classes for sterch.conveyor
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import sterch.logfile
import sterch.queue
import sterch.threading
import zope.app.component
from unittest import TestCase, makeSuite, main
from zope.component.testing import PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig 

class TestSetup(PlacelessSetup, TestCase):
    """Test the various zcml configurations"""
    
    def setUp(self):
        super(TestSetup, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', sterch.threading)()
        XMLConfig('meta.zcml', sterch.queue)()
        XMLConfig('meta.zcml', sterch.logfile)()
        XMLConfig('meta.zcml', sterch.conveyor)()
        XMLConfig('configure.zcml', sterch.threading)()
        XMLConfig('configure.zcml', sterch.queue)()
        XMLConfig('configure.zcml', sterch.logfile)() 
        XMLConfig('configure.zcml', sterch.conveyor)()