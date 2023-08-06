#
#    Copyright (C) 2002-2008  Corporation of Balclutha and contributors.
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
__doc__="""$id$"""
__version__='$Revision: 62 $'[11:-2]


import AccessControl
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.PropertyManager import PropertyManager

try:
    from Products.BastionBase.PortalContent import PortalContent as SimpleItem
except:
    # TODO - test this ;)
    from Products.CMFDefault.Document import Document as SimpleItem


manage_addBastionPGPKeyRecordForm = PageTemplateFile('zpt/add_key', globals()) 
def manage_addBastionPGPKeyRecord(self, id, name, email, comment, key, REQUEST=None):
    """ wrapper for an OpenPGP Key """

    assert self.meta_type == 'BastionPGPKeyZopeRepository', 'Incorrect Container Type!'

    self._setObject(id, BastionPGPKeyRecord(id, name, email, comment, key))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    return id

class BastionPGPKeyRecord(PropertyManager, SimpleItem):
    """
    wrapper for an OpenPGP Key 

    derives of ObjectManager to get all the App.Management mgmt tab stuff ...
    """
    
    meta_type = portal_type ='BastionPGPKeyRecord'

    _security = ClassSecurityInfo()
    __ac_permissions__ = PropertyManager.__ac_permissions__ + SimpleItem.__ac_permissions__
    _properties = PropertyManager._properties + (
	{'id':'name',     'type':'string',  'mode':'r' },
	{'id':'email',    'type':'string',  'mode':'r' },
	{'id':'comment',  'type':'string',  'mode':'r' },
	{'id':'key',      'type':'text',    'mode':'r' },
    )

    manage_options = SimpleItem.manage_options

    def __init__(self, id, name, email,comment, key):
        self.id = id
        self.title = '%s (%s) %s' % (name, comment, email)
        self.name = name
        self.email = email
        self.comment = comment
        self.key = key

    def index_html(self, REQUEST):
	"""download the key"""
        REQUEST.RESPONSE.setHeader('Content-Type', self.aq_parent.mime_type)
        REQUEST.RESPONSE.write(self.key)
	
    def obfuscated_email(self):
	addr, domain = self.email.split('@')
	domains = domain.split('.')
	return '%s at %s' % (addr, ' dot '.join(domains))


AccessControl.class_init.InitializeClass(BastionPGPKeyRecord)
    
