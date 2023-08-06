#
#    Copyright (C) 2002-2012  Corporation of Balclutha and contributors.
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


import AccessControl, transaction
from AccessControl.Permissions import view, change_configuration, access_contents_information
from OFS.SimpleItem import SimpleItem
try:
    from Products.CMFPlone.PloneFolder import PloneFolder as ObjectManager
except:
    from OFS.ObjectManager import ObjectManager

# our local stuff
import os, commands, re, time, logging
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.standard import structured_text, newline_to_br

LOG = logging.getLogger('BastionCertAuthority')

_using_openssl = 0
try:
    import POW
    from  POW import pkix
    LOG.info('using POW')
    
except:
    _using_openssl = 1
    LOG.info('using openssl')

def using_openssl(): return _using_openssl


manage_addBastionCertAuthorityForm = PageTemplateFile('zpt/add_ca', globals()) 
def manage_addBastionCertAuthority(self, id, keyfile='/etc/pki/tls/private/rsa.keydec',
                                   cert='/etc/pki/tls/certs/ca.crt', directory='/tmp',
                                   ca_directory='/tmp',title='', REQUEST=None):
    """ wrapper for an OpenSSL X509 CertAuthority """

    #
    # create the standard structure underneath the ca_directory ...
    # this stuff is all as-per the CA.sh script in the /usr/local/ssl/misc dir ..
    #
    if _using_openssl:
        assert directory and ca_directory, 'You must supply a working directory and a ca directory'
    
    self._setObject(id, BastionCertAuthority(id, title, directory, ca_directory, keyfile, cert))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class BastionCertAuthority(ObjectManager, SimpleItem):
    """
    wrapper for an OpenSSL X509 CertAuthority 

    derives of ObjectManager to get all the App.Management mgmt tab stuff ...
    """
    
    meta_type = portal_type ='BastionCertAuthority'

    manage_options =  (
        {'label': 'Sign',      'action': 'manage_sign' },
        {'label': 'Configure', 'action': 'manage_config' },
        {'label': 'View',      'action': '' },
        ) + SimpleItem.manage_options


    __ac_permissions__= (
        (access_contents_information, ('ca_cert','pretty_ca_certificate')),
        (view, ( 'sign', 'download_ca_cert')),
        (change_configuration, ('manage_config', 'manage_edit')),
        )

        
    def __init__(self, id, title, directory, ca_directory, keyfile, certfile):
        self.id = id
        self._directory = ''
        self._ca_directory = ''
        self.manage_edit(title, directory, ca_directory, keyfile, certfile)
        self._policy = 'policy_anything'

    manage_sign = PageTemplateFile('zpt/sign_cert', globals())
    manage_config = PageTemplateFile('zpt/cert_config', globals())

    def directory(self): return self._directory
    def ca_directory(self): return self._ca_directory
    def keyfile(self): return self._keyfile
    def certfile(self): return self._cert

    def openssl_mode(self): return using_openssl
    
    def manage_edit(self, title='', directory='', ca_directory='', keyfile='', cert='', REQUEST=None):
        """ """
        self.title = title
        self._directory = directory
        if self._ca_directory != directory:
            if _using_openssl:
                self._makeOpenSSLDirs(ca_directory)
            self._ca_directory = ca_directory
        self._cert = cert
        self._keyfile = keyfile
        try:
            delattr(self, '_v_key')
        except:
            pass
        try:
            # validate key ...
            junk = self._key()
        except:
            transaction.get().abort()
            if REQUEST:
                REQUEST.RESPONSE.redirect('%s/manage_config?Bad+RSA+private+key+file' % REQUEST['URL1'])
            raise
        
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_config' % REQUEST['URL1'])
        
    def sign(self, keyfile=None, keytext='', REQUEST={}):
        """ go sign the key - file takes precedence over text ... """

        if not keyfile and not keytext:
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'Please supply either a file or certificate signing request text')
                return self.manage_sign(self, REQUEST)
            raise ValueError, 'keyfile or keytext required'

        if _using_openssl:
            # using self.REQUEST so that controller forms work ;)
            filename = "%s/%s" %  (self._directory, self.REQUEST.SESSION.getId())
            file = open(filename, 'w')
            file.write(keytext or keyfile.read())
            file.close()

            #
            # TODO - fix this demoCA directory shite ...
            #
            command = """cd %s && openssl ca -cert %s -keyfile %s -policy %s -in %s -batch -out %s.pem -outdir %s/newcerts""" % \
                      (self._ca_directory, self._cert, self._keyfile, self._policy, filename, filename, self._ca_directory)

            LOG.debug(command)

            stdin, stdouterr = os.popen4(command, 'r')
            rc = stdouterr.read()

            stdin.close()
            stdouterr.close()

            if os.access('%s.pem' % filename, os.F_OK) and os.stat('%s.pem' % filename)[6] > 0:
                file = open('%s.pem' % filename, 'r')
                self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/octetstream')
                self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename=ca.pem')
                self.REQUEST.RESPONSE.write(file.read())
                file.close()
                os.unlink(filename)
                os.unlink('%s.pem' % filename)
                return 0
            if REQUEST:
                REQUEST.set('manage_tabs_message',
                            structured_text('Error signing certificate - the problem may be highlighted below\n:%s' % rc))
                return self.manage_sign(self, REQUEST)
            else:
                raise ValueError, rc
        else:
            cert = POW.pemRead(POW.X509_CERTIFICATE, key_file.read() )           
            cert.sign(self._key())
            self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/octetstream')
            self.REQUEST.RESPONSE.write( cert.pemWrite() )

    def ca_cert(self):
        """
        return the raw CA certificate
        """
        # cached key ...
        if not hasattr(self, '_v_cert'):
	    try:
                try:
                    fh = open(self._cert , 'r' )
                    self._v_cert = fh.read()
                except:
                    try:
                        fh.close()
                    except:
                        pass
	    except:
	        self._v_cert = None
        return self._v_cert

    def download_ca_cert(self, REQUEST, RESPONSE):
        """
        download the CA Certificate
        """
        RESPONSE.setHeader('Content-Type', 'Application/Octet-Stream')
        RESPONSE.write(self.ca_cert())

    def pretty_ca_certificate(self):
        """
        return an html-formatted text output of the CA certificate
        """
        command = """openssl x509 -in %s -text""" %  self._cert

        stdin,stdouterr = os.popen4(command, 'r')
        rc = stdouterr.read()
        
        stdin.close()
        stdouterr.close()

        return newline_to_br(rc)
        
    def _makeOpenSSLDirs(self, directory):
        """
        create openssl filesystem requirements ...
        """
        if not os.path.exists(directory):
            os.mkdir(directory)

        if not os.path.exists('%s/certs' % directory):
            os.mkdir('%s/certs' % directory)
            
        if not os.path.exists('%s/crl' % directory):
            os.mkdir('%s/crl' % directory)

        if not os.path.exists('%s/newcerts' % directory):
            os.mkdir('%s/newcerts' % directory)


        if not os.path.exists('%s/private' % directory):
            os.mkdir('%s/private' % directory)

        if not os.path.exists('%s/serial' % directory):
            serial = open('%s/serial' % directory, 'w')
            serial.write('01')
            serial.close()

        if not os.path.exists('%s/index.txt' % directory):
            index = open('%s/index.txt' % directory, 'w')
            index.close()


    def _key(self):
        # cached key ...
        if not hasattr(self, '_v_key'):
	    try:
	        if _using_openssl:
	            self._v_key = open(self._keyfile , 'r' ).read()
	        else:
                    self._v_key = POW.pemRead(POW.RSA_PRIVATE_KEY, open(self._keyfile , 'r' ).read() )
	    except:
	        self._v_key = None
        return self._v_key

    def _getPortalTypeName(self):
        """
        needed for the portal type view mechanism ...
        """
        return self.meta_type
     
    def _generate_ca_cert(self, keydec, req):
        """
        generate the CA certificate in the first instance
        """
        # TODO - this is only documentation ...
        if not req:
            req = 'openssl req -new -keyout /tmp/bla.key -out /tmp/bla.pem'

        cmd = 'openssl ca -create_serial -out /tmp/ca.crt -days 3650 -batch -keyfile /tmp/bla.keydec -selfsign -extensions v3_ca -infiles /tmp/bla.req'

AccessControl.class_init.InitializeClass(BastionCertAuthority)
    
