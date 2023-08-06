#
#    Copyright (C) 2002  Corporation of Balclutha and contributors.
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
from Globals import MessageDialog, Persistent, data_dir
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import view, change_configuration
# some other stuff
import Acquisition
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from Products.PythonScripts.standard import structured_text

# our local stuff
import os, sys
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

manage_addBastionPGPKeyGeneratorForm = PageTemplateFile('zpt/add_pgp', globals()) 
def manage_addBastionPGPKeyGenerator(self, id, directory, title='', REQUEST=None):
    """ wrapper for an OpenPGP Public Key """

    self._setObject(id, BastionPGPKeyGenerator(id, title, directory))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    return 0

class BastionPGPKeyGenerator(ObjectManager, SimpleItem):
    """
    wrapper for an OpenPGP Public Key

    derives of ObjectManager to get all the App.Management mgmt tab stuff ...
    """

    meta_type = portal_type ='BastionPGPKeyGenerator'
    _security = ClassSecurityInfo()

    __ac_permissions__= (
        (view, ('manage_page_header', 'manage_page_footer','manage_main',
                  'manage_tabs', 'manage_generate', )),
        (change_configuration, ('manage_config',)),
        )

    manage_options =  (
        {'label': 'Generate', 'action': 'manage_generate' },
        {'label': 'Configure', 'action': 'manage_config' },
    ) + SimpleItem.manage_options

    def __init__(self, id, title, directory):
        self.id = id
        self.title = title
        self._directory = directory

    def directory(self) : return self._directory
        
    manage_generate = PageTemplateFile('zpt/generate_pgp', globals())
    manage_config = PageTemplateFile('zpt/config', globals())

    _security.declareProtected('Change configuration', 'manage_edit')
    def manage_edit(self, title='', directory='', REQUEST=None):
        self.title = title
        if directory != '':
            self._directory = directory
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('%s/manage_config', REQUEST['URL1'])
        
    _security.declareProtected('View', 'generate')
    def generate(self, passphrase1, passphrase2, realname,
                 email, comment, type, size, expires, unit, REQUEST):
        """ go generate the key ... """
        
        if len (realname) < 5:
            return MessageDialog(
                title  = """BastionPGPKeyGenerator""",
                message = """Real Name  must be at least 5 characters.""",
                action = '%s/manage_main' % REQUEST['URL1'])

        if len (passphrase1) < 5:
            return MessageDialog(
                title  = """BastionPGPKeyGenerator""",
                message = """Passphrase must be at least 5 characters.""",
                action = '%s/manage_main' % REQUEST['URL1'])

        if not passphrase1 == passphrase2:
            return MessageDialog(
                title  = """BastionPGPKeyGenerator""",
                message = """Passphrase does not match.""",
                action = '%s/manage_main' % REQUEST['URL1'])

        if size == "0" and not unit == "0":
            return MessageDialog(
                title  = """BastionPGPKeyGenerator""",
                message = """Invalid Expiry combination.""",
                action = '%s/manage_main' % REQUEST['URL1'])

        if unit == "0":
            expires = "0"
        else:
            expires += unit

        dir = "%s/%s" %  (self._directory, REQUEST.SESSION.getId())
        command = """mkdir -p %s && %s/Products/BastionCrypto/gpg.exp %s '%s' '%s' '%s' '%s' %s %s %s 2>&1""" % \
        (dir, INSTANCE_HOME, dir, realname, passphrase1, email,
         comment, type, size, expires)

        syscall = os.popen(command, 'r')
        rc = syscall.read()
        #if rc:
        #    REQUEST.form['error'] = structured_text(rc)
        #    return self.generate_key(self, REQUEST)

        if os.access('%s/pubring.gpg' % dir, os.F_OK) and \
           os.access('%s/secring.gpg' % dir, os.F_OK):
            syscall = os.popen("""cd %s && tar cf - *.gpg && rm -rf %s""" % (dir, dir), 'r')
            REQUEST.RESPONSE.setHeader('Content-Type', 'application/x-tar')
            REQUEST.RESPONSE.write(syscall.read())
            return 

        REQUEST.set('manage_tabs_message',
                    structured_text('Keys not created - the problem may be highlighted below\n:%s' % rc))
        return self.manage_generate(self, REQUEST)
                    
AccessControl.class_init.InitializeClass(BastionPGPKeyGenerator)
