#
#  Copyright (C) 2008-2011  Corporation of Balclutha. All rights Reserved.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# CryptoTestCase
#

# $Id: CryptoTestCase.py 262 2007-11-23 23:34:55Z alan $

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('BastionCrypto')
ZopeTestCase.installProduct('Archetypes')

PloneTestCase.setupPloneSite(products=('BastionCrypto', 'Archetypes'), 
                             extension_profiles=['Products.CMFFormController:CMFFormController',
                                                 'Products.CMFQuickInstallerTool:CMFQuickInstallerTool',
                                                 'Products.MimetypesRegistry:MimetypesRegistry',
                                                 'Products.PortalTransforms:PortalTransforms',
                                                 'Products.Archetypes:Archetypes',
                                                 'Products.Archetypes:Archetypes_sampletypes'])


class CryptoTestCase(PloneTestCase.PloneTestCase):
   """ Base test case for testing BastionCallCentre functionality """

   def afterSetUp(self):   
      self.portal.manage_addProduct['BastionCrypto'].manage_addBastionPGPKeyZopeRepository()
      self.pks = self.portal.pks

