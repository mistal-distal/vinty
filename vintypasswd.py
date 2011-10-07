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
from getpass import getpass
from optparse import OptionParser
import commands, os, os.path, re, sys, tempfile
import pki, pki.util

## Functions ###################################################################
def error(msg):
   sys.stderr.write('Error: ' + msg + '\n')
   sys.exit(1)

# ------------------------------------------------------------------------------
def parse_argv(argv):
   keyfile = ''
   usage   = """%prog --set KEY
       %prog --remove KEY"""
   version = '%prog ' + __version__
   parser  = OptionParser(usage=usage, version=version)
   parser.add_option('--set', action='store_true', default=False,
                     metavar="KEY", help='add a passphrase to KEY')
   parser.add_option('--remove', action='store_true', default=False,
                     metavar="KEY", help='remove the passphrase from KEY')
   opt, arg = parser.parse_args(argv)
   if opt.set and opt.remove:
      parser.error('--set and --remove are mutually exclusive')
   elif opt.set or opt.remove:
      if len(arg) == 1:
         keyfile = arg[0]
      else:
         parser.error('no keyfile given')
   else:
      parser.print_help()
      sys.exit(1)
   return opt, keyfile

# ------------------------------------------------------------------------------
def remove_passphrase(config, keyfile, remove_only=True):
   if remove_only:
      passwd = getpass()
   else:
      passwd = getpass('Old password: ')
   tmpfile = keyfile + '.tmp'
   try:
      fd, fname = tempfile.mkstemp()
      os.write(fd, passwd)
      os.close(fd)
   except:
      sys.stderr.write('Problem creating secure temporary file...\n')
      sys.exit(1)
   else:
      cmd = pki.OPENSSL_COMMANDS['del_passphrase'] \
            % { 'openssl' : config.get('openssl', 'path'),
                'pwfile'  : fname,
                'inkey'   : keyfile,
                'outkey'  : tmpfile
              }
      status, output = commands.getstatusoutput(cmd)
      os.remove(fname)
      if status:
         sys.stderr.write('Problem removing old passphrase:\n' + output)
         sys.exit(1)
      else:
         try:
            os.remove(keyfile)
            os.rename(tmpfile, keyfile)
         except:
            sys.stderr.write('Problem storing new keyfile.\n')

# ------------------------------------------------------------------------------
def set_passphrase(config, keyfile):
   if pki.util.is_encrypted(keyfile):
      remove_passphrase(config, keyfile, remove_only=False)
   pw1     = getpass()
   pw2     = getpass('Retype password: ')
   tmpfile = keyfile + '.tmp'
   if pw1 != pw2:
      sys.stderr.write('Password mismatch.\n')
      sys.exit(1)
   else:
      try:
         fd, fname = tempfile.mkstemp()
         os.write(fd, pw1)
         os.close(fd)
      except:
         sys.stderr.write('Problem creating secure temporary file...\n')
         sys.exit(1)
      else:
         cmd = pki.OPENSSL_COMMANDS['set_passphrase'] \
               % { 'openssl' : config.get('openssl', 'path'),
                   'pwfile'  : fname,
                   'inkey'   : keyfile,
                   'outkey'  : tmpfile
                 }
         status, output = commands.getstatusoutput(cmd)
         os.remove(fname)
         if status:
            sys.stderr.write('Problem setting passphrase:\n' + output)
            sys.exit(1)
         else:
            try:
               os.remove(keyfile)
               os.rename(tmpfile, keyfile)
            except:
               sys.stderr.write('Problem storing new keyfile.\n')

## We're being called as a script ##############################################
if __name__ == '__main__':
   opt, keyfile = parse_argv(sys.argv[1:])
   config  = pki.util.parse_config()
   if not os.path.isfile(keyfile):
      error('Unable to open ' + keyfile + '.\n')
   else:
      if pki.util.is_private_key(keyfile):
         if opt.set:
            print 'Setting passphrase on ' + keyfile
            set_passphrase(config, keyfile)
         else:
            print 'Removing passphrase from ' + keyfile
            if pki.util.is_encrypted(keyfile):
               remove_passphrase(config, keyfile)
            else:
               error(keyfile + ' has no passphrase set.')
      else:
         error(keyfile + ' is not a private key.')
