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

## Imports #####################################################################
import commands, os, sys
import pki
import pki.util
from os import path

## Functions ###################################################################
def check_pki(config):
   keyDir = config.get('keys', 'path')
   if path.isdir(keyDir) and \
      path.isdir(config.get('keys', 'path_revoked')) and \
      path.isfile(path.join(keyDir, config.get('ca', 'name') + '.crt')) and \
      path.isfile(path.join(keyDir, config.get('ca', 'name') + '.key')) and \
      path.isfile(config.get('ca', 'crl')) and \
      path.isfile(path.join(keyDir, 'dh' \
                            + config.get('keys', 'size') + '.pem')) and \
      path.isfile(path.join(keyDir, 'index.txt')):
      rv = True
   else:
      rv = False
   return rv

# ------------------------------------------------------------------------------
def create_pki(config):
   keyDir = config.get('keys', 'path')
   revDir = config.get('keys', 'path_revoked')
   if not check_pki(config):
      try:
         os.makedirs(keyDir, 0700)
         os.makedirs(revDir, 0700)
         fp = open(path.join(keyDir, 'index.txt'), 'w')
         fp.close()
         fp = open(path.join(keyDir, 'serial'), 'w')
         fp.write('01\n')
         fp.close
      except:
         result = False
         msg    = str(sys.exc_info()[1])
      else:
         result, msg = build_ca(config)
         if result:
            result, msg = build_dh(config)
            if result:
               result, msg = gen_crl(config)
   else:
      result = False
      msg    = 'previous installation found'
   return result, msg

# ------------------------------------------------------------------------------
def build_ca(config):
   keyDir    = config.get('keys', 'path')
   cn        = config.get('keys', 'org') + ' CA'
   ca        = config.get('ca', 'name')
   keyFile   = path.join(keyDir, ca + '.key')
   crtFile   = path.join(keyDir, ca + '.crt')
   fd, fname = pki.util.create_ssl_script(config, cn)
   if fd:
      cmd  = pki.OPENSSL_COMMANDS['ca_init'] \
             % { 'openssl' : config.get('openssl', 'path'),
                 'expire'  : config.get('ca', 'expire'),
                 'key'     : keyFile,
                 'crt'     : crtFile,
                 'config'  : config.get('openssl', 'conf')
               }
      os.write(fd, cmd + '\n')
      os.close(fd)
      result, msg = pki.util.run_ssl_script(fname)
      if result:
         os.chmod(keyFile, 0600)
   else:
      result = False
      msg    = 'could not create temporary OpenSSL script'
   return result, msg

# ------------------------------------------------------------------------------
def build_dh(config):
   keyDir  = config.get('keys', 'path')
   keySize = config.get('keys', 'size')
   dhFile  = path.join(keyDir, 'dh' + keySize + '.pem')
   cmd     = pki.OPENSSL_COMMANDS['dh_param'] \
             % { 'openssl' : config.get('openssl', 'path'),
                 'dh'      : dhFile,
                 'keysize' : keySize
               }
   result, msg = commands.getstatusoutput(cmd)
   return not result, msg

# ------------------------------------------------------------------------------
def gen_crl(config):
   crl       = config.get('ca', 'crl')
   keyDir    = config.get('keys', 'path')
   fd, fname = pki.util.create_ssl_script(config)
   if fd:
      cmd = pki.OPENSSL_COMMANDS['gen_crl'] \
            % { 'openssl' : config.get('openssl', 'path'),
                'crl'     : crl,
                'config'  : config.get('openssl', 'conf')
              }
      os.write(fd, cmd + '\n')
      os.close(fd)
      result, msg = pki.util.run_ssl_script(fname)
   else:
      result = False
      msg    = 'could not create temporary OpenSSL script'
   return result, msg

# ------------------------------------------------------------------------------
def create_cert(config, cn, type):
   keyDir  = config.get('keys', 'path')
   csrFile = path.join(keyDir, cn + '.csr')
   crtFile = path.join(keyDir, cn + '.crt')
   keyFile = path.join(keyDir, cn + '.key')
   sslBin  = config.get('openssl', 'path')
   sslCfg  = config.get('openssl', 'conf')
   if not (path.isfile(csrFile) or \
           path.isfile(crtFile) or \
           path.isfile(keyFile)):
      fd, fname = pki.util.create_ssl_script(config, cn)
      if fd:
         data = { 'openssl' : sslBin,
                  'expire'  : config.get('keys', 'expire'),
                  'key'     : keyFile,
                  'csr'     : csrFile,
                  'config'  : sslCfg
                }
         if type == pki.CERT_SERVER:
            cmd = pki.OPENSSL_COMMANDS['server_csr'] % data
         else:
            cmd = pki.OPENSSL_COMMANDS['client_csr'] % data
         os.write(fd, cmd + '\n')
         os.close(fd)
         result, msg = pki.util.run_ssl_script(fname)
         if result:
            result, msg = sign_csr(config, cn, type)
      else:
         result = False
         msg    = 'could not create temporary OpenSSL script'
   else:
      result = False
      msg    = 'common Name already in use'
   return result, msg

# ------------------------------------------------------------------------------
def renew_cert(config, cn, type):
   serial = pki.util.serial_from_cn(config, cn)
   if pki.util.cert_type(config, serial, pki.CERT_VALID) == type:
      result, msg = revoke_cert(config, cn, False)
      if result:
         result, msg = sign_csr(config, cn, type)
   else:
      result = False
      msg    = 'certificate is not of type ' + type
   return result, msg

# ------------------------------------------------------------------------------
def revoke_cert(config, cn, move_all=True):
   serial = pki.util.serial_from_cn(config, cn)
   keyDir = config.get('keys', 'path')
   files  = pki.util.cert_files(config, cn, serial)
   if not files:
      result = False
      msg    = 'not all files related to ' + cn + ' are available'
   else:
      csrFile, crtFile, keyFile, pemFile = files
      caFile    = path.join(keyDir, config.get('ca', 'name') + '.crt')
      sslBin    = config.get('openssl', 'path')
      sslCfg    = config.get('openssl', 'conf')
      fd, fname = pki.util.create_ssl_script(config, cn)
      if fd:
         cmd = pki.OPENSSL_COMMANDS['revoke_crt'] \
               % { 'openssl': sslBin, 'crt': crtFile, 'config': sslCfg }
         #os.write(fd, cmd + ' && ')
         #cmd = pki.OPENSSL_COMMANDS['revoke_verify'] \
         #      % { 'openssl': sslBin, 'ca': caFile, 'crt': crtFile }
         os.write(fd, cmd + '\n')
         os.close(fd)
         result, msg = pki.util.run_ssl_script(fname)
         gen_crl(config) # build a new CRL, even if the revocation failed
         if result:
            if move_all:
               filelist = files
            else:
               filelist = (crtFile, pemFile)
            if not pki.util.move_revoked(config, filelist, serial):
               result = False
               msg    = 'unable to move revoked files'
      else:
         result = False
         msg    = 'could not create temporary OpenSSL script'
   return result, msg

# ------------------------------------------------------------------------------
def sign_csr(config, cn, type):
   sslBin    = config.get('openssl', 'path')
   sslCfg    = config.get('openssl', 'conf')
   keyDir    = config.get('keys', 'path')
   csrFile   = path.join(keyDir, cn + '.csr')
   crtFile   = path.join(keyDir, cn + '.crt')
   keyFile   = path.join(keyDir, cn + '.key')
   caFile    = path.join(keyDir, config.get('ca', 'name') + '.crt')
   fd, fname = pki.util.create_ssl_script(config, cn)
   if fd:
      data = { 'openssl' : sslBin,
               'expire'  : config.get('keys', 'expire'),
               'csr'     : csrFile,
               'crt'     : crtFile,
               'config'  : sslCfg
             }
      if type == pki.CERT_SERVER:
         cmd = pki.OPENSSL_COMMANDS['sign_server_csr'] % data
      else:
         cmd = pki.OPENSSL_COMMANDS['sign_client_csr'] % data
      os.write(fd, cmd + ' && ')
      cmd = pki.OPENSSL_COMMANDS['crt_verify'] \
            % { 'openssl' : sslBin, 'ca' : caFile, 'crt' : crtFile }
      os.write(fd, cmd + '\n')
      os.close(fd)
      result, msg = pki.util.run_ssl_script(fname)
      if result:
         os.chmod(keyFile, 0600)
   else:
      result = False
      msg    = 'could not create temporary OpenSSL script'
   return result, msg

# ------------------------------------------------------------------------------
def list_certs(config, listType, cgi = False):
   keyDir = config.get('keys', 'path')
   dbFile = path.join(keyDir, 'index.txt')
   if cgi:
      crtList = []
   for cert in open(dbFile).readlines():
      status, exp, rev, serial, location, dn = cert[:-1].split('\t', 5)
      exp = '20' + exp[0:2] + '/' + exp[2:4] + '/' + exp[4:6]
      if rev:
         rev = '20' + rev[0:2] + '/' + rev[2:4] + '/' + rev[4:6]
      cn = dn[dn.find('CN=')+3:dn.rfind('/')]
      type = pki.util.cert_type(config, serial, status)
      if status == pki.CERT_VALID and listType in ('all', 'valid'):
         if cgi:
            crtList.append((status, serial, exp, cn, type))
         else:
            print 'Common Name: ' + cn + ' (serial: ' + serial + ')'
            print '\ Certificate type: ' + type +  ', valid until: ' + exp
      elif status == pki.CERT_REVOKED and listType in ('all', 'revoked'):
         if cgi:
            crtList.append((status, serial, rev, cn, type))
         else:
            print 'Common Name: ' + cn + ' (serial: ' + serial + ')'
            print '\ Certificate type: ' + type + ', revoked on: ' + rev 
      elif status == pki.CERT_EXPIRED and listType == 'all':
         if cgi:
            crtList.append((status, serial, exp, cn, type))
         else:
            print 'Common Name: ' + cn + ' (serial: ' + serial + ')'
            print '\ Certificate type: ' + type + ', expired on: ' + exp
   if cgi:
      rv = crtList
   else:
      rv = True
   return rv
