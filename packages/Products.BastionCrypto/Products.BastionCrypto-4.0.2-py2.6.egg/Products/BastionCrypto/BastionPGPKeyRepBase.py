#
#    Copyright (C) 2002-2005  Corporation of Balclutha.
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
from AccessControl.Permissions import view, change_configuration
from App.Common import rfc1123_date
from Products.CMFCore.utils import getToolByName
try:
    from Products.BastionBase.BSimpleItem import BSimpleItem as SimpleItem
except:
    from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PythonScripts.standard import url_quote
from Permissions import add_pgp_keys
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BastionPGPKey import BastionPGPKey

class BastionPGPKeyRepBase(PropertyManager, SimpleItem):
    """
    
    The base class for key repository backends
    
    """
    __ac_permissions__= PropertyManager.__ac_permissions__ + (
        (view, ('lookup', 'manage_search',)),
        (add_pgp_keys, ('manage_addkey', 'add', 'add_bastioncrypto',)),
    ) + SimpleItem.__ac_permissions__

    _properties = PropertyManager._properties + (
       {'id':'directory',       'type':'string',  'mode':'w' },
       {'id':'mime_type',       'type':'string',  'mode':'w' },
       {'id':'obfuscate_email', 'type':'boolean', 'mode':'w' },
    )

    manage_options =  (
        {'label': 'Search',     'action': 'manage_search' },
        {'label': 'Add Key',    'action': 'manage_addkey' },
        {'label': 'Properties', 'action': 'manage_propertiesForm' },
    ) + SimpleItem.manage_options


    def __init__(self, id, title, directory):
        self.id = id
        self.title = title
        self.directory = directory
	self.mime_type = 'application/x-pgp'
        self.obfuscate_email = 1

    manage_search = PageTemplateFile('zpt/search', globals())
    manage_addkey = PageTemplateFile('zpt/add_key', globals())

    def all_meta_types(self):
        return ( { 'action' : 'manage_addProduct/BastionCrypto/addBastionPGPKeyRecord'
                 , 'permission' : 'Add BastionCryptoPGPKeyRecord'
                 , 'name' : 'PGPKey Record'
                 , 'Product' : 'BastionCrypto'
                 , 'instance' : BastionPGPKeyRecord
                 },
            )

    def add(self, keyfile='', keytext='', REQUEST=None):
        """ """
        if keytext == '' and keyfile == '':
            return self._error("You must provide a public key, either text or upload file!", REQUEST)
        
        #
        # the key will either be straight text or a file handle ...
        #
        if keytext == '':
            if keyfile.filename == "":
                return self._error("You must supply your public key file!", REQUEST)
            keytext = keyfile.read()

        key = BastionPGPKey(keytext)

        if not key.isValid():
            return self._error("""Woa - this doesn't appear to be a GPG Key (%s)""" % keytext, REQUEST)
            
        try:
            self._addkey(key)
        except Exception, e:
            return self._error(str(e), REQUEST)

	if REQUEST:
	    REQUEST.set('manage_tabs_message', 'Successfully added key')
	    REQUEST.set('management_view', 'Add Key')
	    return self.manage_addkey(self, REQUEST)

    def lookup(self, op='get', keyid='', REQUEST=None):
        """ download key to local machine ... """
        assert op in ['get', 'index'], "Bad op!"
        if op == 'get':
            key = self._getkey(keyid)
            if REQUEST:
                REQUEST.RESPONSE.setHeader('Content-Type', self.mime_type)
                REQUEST.RESPONSE.write(key)
            return key
        else:
	    # hmmm, this should be a list ...
            keys = self._getkeys(keyid)
            if REQUEST:
                REQUEST.RESPONSE.setHeader('Content-Type', self.mime_type)
                REQUEST.RESPONSE.write(string.join(keys, '\n'))
            return keys
        
    def _error(self, msg, REQUEST=None):
        if REQUEST is None:
            raise AttributeError, msg
        else:
            REQUEST.set('management_view', 'Add Key')
            REQUEST.set('manage_tabs_message', msg)
            return self.manage_addkey(self, REQUEST)
        
    def _addkey(self, bastionpgpkey):
        raise NotImplementedError

    def _getkey(self, keyid):
        raise NotImplementedError

    def _getkeys(self, keyids):
        raise NotImplementedError

    def add_bastioncrypto(self, REQUEST, RESPONSE):
	"""
	use the bastioncrypto helper application to export your key
	"""
	# much of this code is from the ExternalEditor product ...
        r = []

        r.append('url:%s' % self.absolute_url())
	key_id = getToolByName(self, 'portal_membership').getAuthenticatedMember().email
        r.append("""arguments:--export --armor -u '<%s>'""" % key_id)
        #r.append("""arguments:--export --armor""")

        if REQUEST._auth[-1] == '\n':
            auth = REQUEST._auth[:-1]
        else:
            auth = REQUEST._auth
        r.append('auth:%s' % auth)
        r.append('cookie:%s' % REQUEST.environ.get('HTTP_COOKIE',''))
        r.append('')
        
        RESPONSE.setHeader('Last-Modified', rfc1123_date())

        RESPONSE.setHeader('Content-Type', 'application/x-bastioncrypto')
        # Using RESPONSE.setHeader('Pragma', 'no-cache') would be better, but
        # this chokes crappy most MSIE versions when downloads happen on SSL.
        # cf. http://support.microsoft.com/support/kb/articles/q316/4/31.asp

	return '\n'.join(r)

    def PUT(self, REQUEST, RESPONSE):
	"""
	return packet from our bastioncrypto ...
	"""
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)

	self.add(keytext=REQUEST['BODYFILE'].read())

        RESPONSE.setStatus(204)
        return RESPONSE
        
AccessControl.class_init.InitializeClass(BastionPGPKeyRepBase)
