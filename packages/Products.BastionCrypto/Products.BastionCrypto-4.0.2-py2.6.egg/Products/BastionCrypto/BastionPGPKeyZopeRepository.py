#
#    Copyright (C) 2002-2012  Corporation of Balclutha.
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
__version__='$Revision: 67 $'[11:-2]


import AccessControl, Products
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import view, change_configuration
from Products.CMFCore.permissions import View, ModifyPortalContent
from Permissions import add_pgp_keys

# some other stuff
import Acquisition
try:
    from Products.BastionBase.LargePortalFolder import LargePortalFolder as BTreeFolder2
except:
    raise
    try:
	from Products.CMFPlone.LargePloneFolder import LargePloneFolder as BTreeFolder2
    except:
        from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

from Products.ATContentTypes.content.document import ATDocument as Document
#try:
#    from Products.CMFDefault.Document import Document
#except:
#    from OFS.SimpleItem import SimpleItem as Document
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.PythonScripts.standard import url_quote

# our local stuff
import os, sys, re, tempfile, commands, time
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from BastionPGPKeyRepBase import BastionPGPKeyRepBase
from OFS.userfolder import manage_addUserFolder, UserFolder
from BastionPGPKeyRecord import manage_addBastionPGPKeyRecord

from config import TEXTINDEX

manage_addBastionPGPKeyZopeRepositoryForm = PageTemplateFile('zpt/add_pgp_zope', globals()) 
def manage_addBastionPGPKeyZopeRepository(self, id='pks', title='Key Server',
                                          directory='/tmp', REQUEST=None):
    """ wrapper for an OpenPGP Public Key """

    self._setObject('pks', BastionPGPKeyZopeRepository('pks', title, directory))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    return 'pks'

class BastionPGPKeyZopeRepository(BTreeFolder2, ZCatalog, BastionPGPKeyRepBase, Document):
    """ wrapper for an OpenPGP Public Key """

    meta_type = portal_type ='BastionPGPKeyZopeRepository'
    _security = ClassSecurityInfo()
    _properties = BastionPGPKeyRepBase._properties 
    __ac_permissions__ = BTreeFolder2.__ac_permissions__ + ZCatalog.__ac_permissions__ + \
			 BastionPGPKeyRepBase.__ac_permissions__ + Document.__ac_permissions__

    manage_options = (
	BTreeFolder2.manage_options[0],
        {'label': 'View', 'action':''},
    ) + BastionPGPKeyRepBase.manage_options[0:3] + ZCatalog.manage_options[3:]

    schema = Document.schema

    def __init__(self, id, title='KeyServer', directory='/tmp'):
        BTreeFolder2.__init__(self, id, title)
        BastionPGPKeyRepBase.__init__(self, id, title, directory)
        ZCatalog.__init__(self, id, title)
	Document.__init__(self, id)
        for name in ('id', 'meta_type'):
            self.addIndex(name, 'FieldIndex')
            self.addColumn(name)
        for name in ('name', 'comment', 'email'):
            self.addIndex(name, TEXTINDEX)
            self.addColumn(name)

    def _getkeys(self, keyids):
        """
        search Zope Directory for keys
        """
	results = self.searchResults(id=keyids)
        return map(None, map(lambda x: x['id'], results), results)

    
    def _addkey(self, bastionpgpkey, REQUEST=None):
        """ """
	name, comment, email = bastionpgpkey.pgpNameCommentEmail()
        id = manage_addBastionPGPKeyRecord(self, bastionpgpkey.pgpKeyId(), name, email, comment, bastionpgpkey._v_key)

    def _getkey(self, id):
	try:
            return self._getOb(id)
	except:
	    raise KeyError, id

    PUT = BastionPGPKeyRepBase.PUT

    def _delObject(self, id, dp=1):
	object=self._getOb(id)
	if object.meta_type == 'BastionPGPKeyRecord':
            self.uncatalog_object('/'.join(object.getPhysicalPath()))
	BTreeFolder2._delObject(self, id)

    def _setObject(self, id,object,roles=None,user=None, set_owner=1):
        BTreeFolder2._setObject(self, id,object,roles,user, set_owner)
	if object.meta_type == 'BastionPGPKeyRecord':
            self.catalog_object(object, '/'.join(object.getPhysicalPath()))

    def ZopeFindAndApply(self, obj, obj_ids=None, obj_metatypes=None,
                         obj_searchterm=None, obj_expr=None,
                         obj_mtime=None, obj_mspec=None,
                         obj_permission=None, obj_roles=None,
                         search_sub=0,
                         REQUEST=None, result=None, pre='',
                         apply_func=None, apply_path=''):
        # seems BTree objectItems is screwed - and we're ignoring the parameters!!
        apply_path = '/'.join(self.getPhysicalPath())
        for obj in self.objectValues('BastionPGPKeyRecord'):
            self.catalog_object(obj, '%s/%s' % (apply_path, obj.getId()))

AccessControl.class_init.InitializeClass(BastionPGPKeyZopeRepository)

