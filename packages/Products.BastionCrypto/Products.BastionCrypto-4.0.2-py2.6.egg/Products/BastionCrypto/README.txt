This is the BastionCrypto cryptography tools for ZOPE, the Z Object Publishing 
Environment (http://www.zope.org/)

This is a simple GUI API to the popular GnuPG (http://www.gnupg.org) and OpenSSL
(http://www.openssl.org) suites.  

There are two basic modes of operation depending upon what is available on your
system:
   pure Python
   expect/TCL

For the X509 suite, if the POW module (http://www.sourceforge.net/POW) is 
available, then it is used, otherwise a call to expect is made.
It simply uses the expect utility to emulate command-line processing for these
suites.



Installation
------------

Unpack it in your Zope Products directory. This should create a directory
named /ZOPE/lib/python/Products/BastionCrypto/ containing the product files as well 
as this README file.

System prerequisites for this suite are (you probably don't need to take the 
versions too seriously):
   openssl-0.9.6/0.9.7
   tcl-8.3.1-53
   expect-5.32
   POW-0.7

   gnupg-1-0.6-5

Usage
-----

The suite is completely self-contained within the Zope framework - Enjoy!

If you want to use the gpg --send-keys / --recv-keys functionality with the keyserver
option set in .gnupg/options, then you additionally need your http server listening
on port 11371 and delegating directly to the parent of your pks object.

For example, if using Apache as a front-end to Zope (and there are many good
reasons for this!!), you should include a VirtualHost directive (and corresponding 
Listen 11371 entry) similar to:

<VirtualHost *:11371>
      DocumentRoot  /dev/null
      ServerAdmin   gatekeeper@last-bastion.net
      ServerName    www.last-bastion.net
      ErrorLog      logs/last-bastion.net_error_log
      CustomLog     logs/last-bastion.net_access_log common
   
      RewriteEngine on
      RewriteRule ^/(.*)$ http://localhost:8080/VirtualHostBase/http/www.last-bastion.net/keyserver/$1 [L,P]
</VirtualHost>

This corresponds to a GPG keyserver directive of www.last-bastion.net.

If using LDAP for your key repository, you may need to add an ldap entry.  There is a sample ldif 
file in schema/setup.ldif.  The pgpServerInfo schema is included in the schema/pgp-keyserver.schema 
file.

NOTE
----
Some problems have been noted with the expect scripts where they refuse to exit.
This is apparent by discerning a pty still open and it's chain of parent processes
in a wait state.  Using the -nottyinit expect flag will resolve this problem.  This
is documented in the expect scripts.  You are strongly advised to install POW.


