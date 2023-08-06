#
#    Copyright (C) 2002-2011  Corporation of Balclutha.  All rights Reserved.
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
__version__='$Revision: 65 $'[11:-2]

import BastionX509Generator, BastionPGPKeyRecord, BastionPGPKeyZopeRepository
import SignedDocument
import BastionCertAuthority

from config import *

from App.ImageFile import ImageFile
# ldap is optional as it's a bit more complex to set up ...
try:
    import BastionPGPKeyLDAPRepository
except:
    pass

from Permissions import add_crypto_utils, add_pgp_keys

# plone stuff
try:
    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.CMFCore import utils
    registerDirectory(SKINS_DIR, GLOBALS)
except:
    pass

def initialize(context): 
    context.registerClass(BastionX509Generator.BastionX509Generator,
                          permission = add_crypto_utils,
                          constructors = (BastionX509Generator.manage_addBastionX509GeneratorForm,
                                          BastionX509Generator.manage_addBastionX509Generator),
                          icon='www/x509.gif',
                        )
    #context.registerClass(BastionPGPKeyGenerator.BastionPGPKeyGenerator,
    #                      permission = add_crypto_utils,
    #                      constructors = (BastionPGPKeyGenerator.manage_addBastionPGPKeyGeneratorForm,
    #                                      BastionPGPKeyGenerator.manage_addBastionPGPKeyGenerator),
    #                      icon='www/pgp.gif',
    #                    )
    try:
        context.registerClass(BastionPGPKeyLDAPRepository.BastionPGPKeyLDAPRepository,
                              permission = add_crypto_utils,
                              constructors = (BastionPGPKeyLDAPRepository.manage_addBastionPGPKeyLDAPRepositoryForm,
                                              BastionPGPKeyLDAPRepository.manage_addBastionPGPKeyLDAPRepository),
                              icon='www/pgp_repository.gif',
                              )
    except:
        pass
    context.registerClass(BastionPGPKeyZopeRepository.BastionPGPKeyZopeRepository,
                          permission = add_crypto_utils,
                          constructors = (BastionPGPKeyZopeRepository.manage_addBastionPGPKeyZopeRepositoryForm,
                                          BastionPGPKeyZopeRepository.manage_addBastionPGPKeyZopeRepository),
                          icon='www/pgp_repository.gif',
                        )
    context.registerClass(BastionCertAuthority.BastionCertAuthority,
                          permission = add_crypto_utils,
                          constructors = (BastionCertAuthority.manage_addBastionCertAuthorityForm,
                                          BastionCertAuthority.manage_addBastionCertAuthority),
                          icon='www/ca.gif',
                        )
    context.registerClass(BastionPGPKeyRecord.BastionPGPKeyRecord,
                          permission = add_pgp_keys,
                          visibility = None,
                          constructors = (BastionPGPKeyRecord.manage_addBastionPGPKeyRecordForm,
                                          BastionPGPKeyRecord.manage_addBastionPGPKeyRecord),
                          icon='www/pgp_rec.gif',
                        )
    context.registerHelp()
    try:
        utils.ContentInit(PROJECTNAME + ' Content',
                          content_types = [],
                          extra_constructors = (
            BastionX509Generator.manage_addBastionX509Generator,
            BastionPGPKeyZopeRepository.manage_addBastionPGPKeyZopeRepository,
            SignedDocument.addSignedDocument,
            BastionCertAuthority.manage_addBastionCertAuthority,
            ),
                          permission = add_crypto_utils,
                          fti = [],).initialize(context)
    except:
        pass



misc_ = {}
for icon in ('pgp_repository', 'x509', 'pgp', 'ca', 'pgp_rec', 'signed_document_icon'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, globals())

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products').declarePublic('BastionCrypto')

ModuleSecurityInfo('Products.BastionCrypto').declarePublic('BastionPGPKey')
ModuleSecurityInfo('Products.BastionCrypto.BastionPGPKey').declarePublic('BastionPGPKey')

ModuleSecurityInfo('Products.BastionCrypto').declarePublic('BastionCertAuthority')
ModuleSecurityInfo('Products.BastionCrypto.BastionCertAuthority').declarePublic('using_openssl')
