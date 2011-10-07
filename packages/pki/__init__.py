#!/usr/bin/python

## Revision history ############################################################
__author__  = 'Wouter Eerdekens <info@fks.be>'
__date__    = '2011-08-12'
__version__ = 0.1
__history__ = """
2011-08-12 - Prepare for initial release <jeroen.hooyberghs@fks.be>
2006-07-26 - initial version.
"""
################################################################################

# -- Certificate types
CERT_SERVER  = 'server'
CERT_CLIENT  = 'client'

# -- Certificate status types
CERT_VALID   = 'V'
CERT_REVOKED = 'R'
CERT_EXPIRED = 'E'

# -- Dictionary containing all required openssl commands
OPENSSL_COMMANDS = { 
'ca_init'         : '%(openssl)s req -batch -days %(expire)s -nodes -new' \
                    + ' -x509 -keyout %(key)s -out %(crt)s -config %(config)s',
'dh_param'        : '%(openssl)s dhparam -out %(dh)s %(keysize)s',
'client_csr'      : '%(openssl)s req -batch -days %(expire)s -nodes -new' \
                    + ' -keyout %(key)s -out %(csr)s -config %(config)s',
'server_csr'      : '%(openssl)s req -batch -days %(expire)s -nodes -new' \
                    + ' -extensions server -keyout %(key)s -out %(csr)s' \
                    + ' -config %(config)s',
'sign_client_csr' : '%(openssl)s ca -batch -days %(expire)s -in %(csr)s' \
                    + ' -out %(crt)s -config %(config)s',
'sign_server_csr' : '%(openssl)s ca -batch -days %(expire)s -in %(csr)s' \
                    + ' -out %(crt)s -extensions server -config %(config)s',
'crt_verify'      : '%(openssl)s verify -CAfile %(ca)s %(crt)s',
'revoke_crt'      : '%(openssl)s ca -revoke %(crt)s -config %(config)s',
'revoke_verify'   : '%(openssl)s verify -CAfile %(ca)s -crl_check %(crt)s',
'gen_crl'         : '%(openssl)s ca -gencrl -out %(crl)s -config %(config)s',
'del_passphrase'  : '%(openssl)s rsa -passin file:%(pwfile)s' \
                    + ' -in %(inkey)s -out %(outkey)s',
'set_passphrase'  : '%(openssl)s rsa -passout file:%(pwfile)s -des3' \
                    + ' -in %(inkey)s -out %(outkey)s'
}
