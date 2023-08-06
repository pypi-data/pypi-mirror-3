#
#    Copyright (C) 2009  Corporation of Balclutha.  All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from unittest import TestCase, TestSuite, makeSuite
from Testing import ZopeTestCase  # this fixes up PYTHONPATH :)


from Products.BastionCrypto import BastionX509Generator



class TestX509(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        # hmmm ZTC has screwed up SOFTWARE_HOME/INSTANCE_HOME
        BastionX509Generator.manage_addBastionX509Generator(self.app.test_folder_1_, 'x509')
	self.x509 = self.app.test_folder_1_.x509

    def testCreated(self):
        self.failUnless(hasattr(self.app.test_folder_1_, 'x509'))
    
    def XtestGenerate(self):
	self.pks.generate()
	self.assertEqual(key.getId(), '846B1B0423636051')

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestX509))
        return suite

