#!/usr/bin/python

## Revision history ############################################################
__author__  = 'Wouter Eerdekens <we@fks.be>'
__date__    = '2011-08-12'
__version__ = '0.1'
__history__ = """
2011-08-12 - Prepare for initial release <jeroen.hooyberghs@fks.be>
2006-07-26 - initial version.

This code provides the functions available via the 'main' page.
"""

## Imports #####################################################################
import cgi, cgitb
import commands, os, sys, tempfile, zipfile
from os import path
import pki, pki.util, pki.cmd, pki.cgi

## Functions ###################################################################
def create_cert(form, config):
   cn = pki.util.strip_invalid(form['cn'].value)
   if not cn:
      pki.cgi.start_html('Invalid common name', True)
      pki.cgi.show_error('Please specify a valid common name.')
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()
   else:
      type = form['type'].value
      result, msg = pki.cmd.create_cert(config, cn, type)
      if result:
         serial = pki.util.serial_from_cn(config, cn)
         pki.cgi.start_html('Certificate creation complete')
         pki.cgi.show_cert_info([('Common name', cn),
                                 ('Serial', serial),
                                 ('Certificate type', type)])
         pki.cgi.show_link('OK')
         pki.cgi.end_html()
      else:
         pki.cgi.start_html('Certificate creation failed', True)
         pki.cgi.show_error('<pre>' + msg + '</pre>')
         pki.cgi.show_link('Go Back')
         pki.cgi.end_html()

# ------------------------------------------------------------------------------
def download_cert(form, config):
   cn     = form['cn'].value
   serial = pki.util.serial_from_cn(config, cn)
   files  = pki.util.cert_files(config, cn, serial, True)
   try:
      name = path.join(tempfile.mkdtemp(), cn + '.zip')
      zip  = zipfile.ZipFile(name, 'w')
      for file in files:
         zip.write(file, path.basename(file))
      zip.close()
   except:
      pki.cgi.start_html('Internal error', True)
      pki.cgi.show_error(str(sys.exc_info()[1]))
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()
   else:
      print 'Content-Type: application/zip'
      print 'Content-Disposition: attachment;filename=' + cn + '.zip'
      print
      print open(name).read()
      os.remove(name)
      os.rmdir(path.dirname(name))

# ------------------------------------------------------------------------------
def renew_cert(form, config):
   cn          = form['cn'].value
   oldserial   = pki.util.serial_from_cn(config, cn)
   type        = pki.util.cert_type(config, oldserial, pki.CERT_VALID)
   result, msg = pki.cmd.renew_cert(config, cn, type)
   if result:
      newserial = pki.util.serial_from_cn(config, cn)
      pki.cgi.start_html('Certificate renewal complete')
      pki.cgi.show_cert_info([('Common name', cn),
                              ('Old serial', oldserial),
                              ('New serial', newserial),
                              ('Certificate type', type)])
      pki.cgi.show_link('OK')
      pki.cgi.end_html()
   else:
      pki.cgi.start_html('Certificate renewal failed', True)
      pki.cgi.show_error(msg)
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()

# ------------------------------------------------------------------------------
def revoke_cert(form, config):
   cn     = form['cn'].value
   serial = pki.util.serial_from_cn(config, cn)
   type   = pki.util.cert_type(config, serial, pki.CERT_VALID)
   result, msg = pki.cmd.revoke_cert(config, cn)
   if result:
      pki.cgi.start_html('Certificate revocation complete')
      pki.cgi.show_cert_info([('Common name', cn),
                              ('Serial', serial),
                              ('Certificate type', type)])
      pki.cgi.show_link('OK')
      pki.cgi.end_html()
   else:
      pki.cgi.start_html('Certificate revocation failed', True)
      pki.cgi.show_error(msg)
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()

# ------------------------------------------------------------------------------
def pw_add(form, config):
   """
   pw_add : add password to certificate key
   """
   cn     = form['cn'].value
   if form.has_key('password') : 
      pw     = form['password'].value
   else :
      pw = ''
   keyDir = config.get('keys', 'path')
   keyFile = path.join(keyDir,cn + '.key')
   tmpFile = keyFile + '.tmp'
   if pki.util.is_private_key(keyFile) :
      if not pki.util.is_encrypted(keyFile) :
         try:
            pwFd, pwFname = tempfile.mkstemp()
            os.write(pwFd, pw)
            os.close(pwFd)
         except:
            sys.stderr.write('Problem creating secure temporary file...\n')
            sys.exit(1)
         else:
            cmd = pki.OPENSSL_COMMANDS['set_passphrase'] \
                  % { 'openssl' : config.get('openssl', 'path'),
                      'pwfile'  : pwFname,
                      'inkey'   : keyFile,
                      'outkey'  : tmpFile
                    }
            status, output = commands.getstatusoutput(cmd)
            os.remove(pwFname)
            if status:
               pki.cgi.start_html('Password addition')
               pki.cgi.show_error(output)
               pki.cgi.show_link('Go Back')
               pki.cgi.end_html()
               sys.stderr.write('Problem setting passphrase:\n' + output)
            else:
               try:
                  os.remove(keyFile)
                  os.rename(tmpFile, keyFile)
                  pki.cgi.start_html('Password added')
                  pki.cgi.show_link('OK')
                  pki.cgi.end_html()
               except:
                  sys.stderr.write('Problem storing new keyFile ' + keyFile + '\n')
      else :
         output = keyFile + ' is password protected : first remove password'
         pki.cgi.start_html('Password addition')
         pki.cgi.show_error(output)
         pki.cgi.show_link('Go Back')
         pki.cgi.end_html()
   else :
      output = keyFile + ' is not a key : software error'
      pki.cgi.start_html('Password addition')
      pki.cgi.show_error(output)
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()

# ------------------------------------------------------------------------------
def pw_remove(form, config):
   """
   pw_remove : remove password from certificate key
   """
   cn     = form['cn'].value
   if form.has_key('password') : 
      pw     = form['password'].value
   else :
      pw = ''
   keyDir = config.get('keys', 'path')
   keyFile = path.join(keyDir,cn + '.key')
   tmpFile = keyFile + '.tmp'
   if pki.util.is_private_key(keyFile) :
      if pki.util.is_encrypted(keyFile) :
         try:
            pwFd, pwFname = tempfile.mkstemp()
            os.write(pwFd, pw)
            os.close(pwFd)
         except:
            sys.stderr.write('Problem creating secure temporary file...\n')
            sys.exit(1)
         else:
            cmd = pki.OPENSSL_COMMANDS['del_passphrase'] \
                  % { 'openssl' : config.get('openssl', 'path'),
                      'pwfile'  : pwFname,
                      'inkey'   : keyFile,
                      'outkey'  : tmpFile
                    }
            status, output = commands.getstatusoutput(cmd)
            os.remove(pwFname)
            if status:
               pki.cgi.start_html('Password removal')
               pki.cgi.show_error('Wrong password : decryption failed')
               pki.cgi.show_link('Go Back')
               pki.cgi.end_html()
            else:
               try:
                  os.remove(keyFile)
                  os.rename(tmpFile, keyFile)
                  pki.cgi.start_html('Password removed')
                  pki.cgi.show_link('OK')
                  pki.cgi.end_html()
               except:
                  sys.stderr.write('Problem storing new keyFile ' + keyFile + '\n')
      else :
         output = keyFile + ' is not password protected'
         pki.cgi.start_html('Password removal')
         pki.cgi.show_error(output)
         pki.cgi.show_link('Go Back')
         pki.cgi.end_html()
   else :
      output = keyFile + ' is not a key : software error'
      pki.cgi.start_html('Password removal')
      pki.cgi.show_error(output)
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()

# ------------------------------------------------------------------------------
def publish_crl(config):
   if config.has_section('scripts') and \
      config.has_option('scripts', 'publish_crl'):
      script = config.get('scripts', 'publish_crl')
      if path.isfile(script):
         crl = config.get('ca','crl')
         status, output = commands.getstatusoutput(script + ' ' + crl)
         if status:
            pki.cgi.start_html('Problem executing script', True)
            pki.cgi.show_error(output)
            pki.cgi.show_link('Go Back')
            pki.cgi.end_html()
         else:
            pki.cgi.start_html('Certificate Revocation List published')
            pki.cgi.show_info('The script to publish the Certificate' \
                              + ' Revocation List completed successfully.')
            pki.cgi.show_link('OK')
            pki.cgi.end_html()
      else:
         pki.cgi.start_html('Script not found', True)
         pki.cgi.show_error('The script to publish the Certificate' \
                            + ' Revocation list cannot be found.')
         pki.cgi.show_link('Go Back')
         pki.cgi.end_html()
   else:
      pki.cgi.start_html('Configuration error', True)
      pki.cgi.show_error('The current configuration doesn\'t have a script' \
                         + ' configured to publish the Certificate Revocation' \
                         + ' List.')
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()

# ------------------------------------------------------------------------------
def show_cert_db(config):
   pki.cgi.start_html('Vinty PKI Certificate Database')
   pki.cgi.show_cert_db(config)
   pki.cgi.show_link('Go Back')
   pki.cgi.end_html()

# ------------------------------------------------------------------------------
def show_con_file(config):
   pki.cgi.start_html('OpenVPN Connection Status')
   pki.cgi.show_con_file(config)
   pki.cgi.show_link('Go Back')
   pki.cgi.end_html()

# ------------------------------------------------------------------------------
def show_log_file(config):
   """
   show last lines from openvpn.log
   """
   pki.cgi.start_html('OpenVPN Log')
   pki.cgi.show_log_file(config)
   pki.cgi.show_link('Go Back')
   pki.cgi.end_html()

## We're being called as a script ##############################################
if __name__ == '__main__':
   cgitb.enable()
   config = pki.util.parse_config()
   if not config:
      pki.cgi.start_html('Error parsing configuration', True)
      pki.cgi.show_error('There was an error parsing the vinty' \
                         + ' configuration. Please check your setup.')
      pki.cgi.end_html()
   else:
      form = cgi.FieldStorage()
      if form.has_key('action'):
         action = pki.util.strip_invalid(form['action'].value)
      else:
         action = None
      if action == 'create':
         create_cert(form, config)
      elif action == 'download':
         download_cert(form, config)
      elif action == 'renew':
         renew_cert(form, config)
      elif action == 'revoke':
         revoke_cert(form, config)
      elif action == 'p_add':
         pw_add(form, config)
      elif action == 'p_remove':
         pw_remove(form, config)
      elif action == 'publish':
         publish_crl(config)
      elif action == 'show':
         show_cert_db(config)
      elif action == 'con_show':
         show_con_file(config)
      elif action == 'log_show':
         show_log_file(config)
      else:
         pki.cgi.start_html('Invalid call', True)
         pki.cgi.show_error('You cannot use this script directly.')
         pki.cgi.show_error(action)
         pki.cgi.show_link('Go Back')
         pki.cgi.end_html()
