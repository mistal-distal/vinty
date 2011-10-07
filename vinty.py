#!/usr/bin/python

## Revision history ############################################################
## Revision history ############################################################
__author__  = 'Wouter Eerdekens <info@fks.be>'
__date__    = '2011-08-12'
__version__ = '0.1'
__history__ = """
2011-08-12 - Prepare for initial release <jeroen.hooyberghs@fks.be>
2006-07-26 - initial version.
"""
## Imports #####################################################################
import os, sys
from os import path
from optparse import OptionParser
import pki.cmd, pki.util

## Functions ###################################################################
def error(msg):
   sys.stderr.write('Error: ' + msg + '\n')
   sys.exit(1)

# ------------------------------------------------------------------------------
def parse_argv(argv):
   cn      = ''
   usage   = """%prog --init
       %prog --create client|server CN
       %prog --renew client|server CN
       %prog --revoke CN
       %prog --list valid|revoked|all"""
   version = '%prog ' +  __version__
   parser  = OptionParser(usage=usage, version=version)
   parser.add_option('--init', action='store_true', default=False,
                     help='initialise the PKI infrastructure')
   parser.add_option('--list', metavar='TYPE', type='choice',
                     choices=('valid', 'revoked', 'all'),
                     help='list all certificates of TYPE')
   parser.add_option('--create', metavar='TYPE', type='choice',
                     choices=(pki.CERT_CLIENT, pki.CERT_SERVER),
                     help='create a certificate/key pair of TYPE')
   parser.add_option('--renew', metavar='TYPE', type='choice',
                     choices=(pki.CERT_CLIENT, pki.CERT_SERVER),
                     help='renew a certificate of TYPE')
   parser.add_option('--revoke', action='store_true', default=False,
                     help='revoke a certificate')
   opt, arg = parser.parse_args(argv)
   if opt.init:
      if opt.create or opt.renew or opt.revoke or opt.list:
         parser.error('--init cannot be combined with other options')
      if len(arg) != 0:
         parser.error('--init doesn\'t take an argument')
   elif opt.list:
      if opt.init or opt.create or opt.renew or opt.revoke:
         parser.error('--list cannot be combined with other options')
      if len(arg) != 0:
         parser.error('--list doesn\'t take extra arguments')
   elif opt.create:
      if opt.init or opt.list or opt.renew or opt.revoke:
         parser.error('--create cannot be combined with other options')
      if len(arg) == 1:
         cn = arg[0]
      else:
         parser.error('--create requires you to specify a CN')
   elif opt.renew:
      if opt.init or opt.create or opt.revoke or opt.list:
         parser.error('--renew cannot be combined with other options')
      if len(arg) == 1:
         cn = arg[0]
      else:
         parser.error('--renew requires you to specify a CN')
   elif opt.revoke:
      if opt.init or opt.create or opt.renew or opt.list:
         parser.error('--revoke cannot be combined with other options')
      if len(arg) == 1:
         cn = arg[0]
      else:
         parser.error('--revoke requires you to specify a CN')
   else:
      parser.print_help()
      sys.exit(1)
   return opt, cn

# ------------------------------------------------------------------------------
def info(msg):
   sys.stdout.write(msg)
   sys.stdout.flush()

# ------------------------------------------------------------------------------
def pki_init(config):
   sys.stdout.write('Creating PKI infrastructure: ')
   sys.stdout.flush()
   result, msg = pki.cmd.create_pki(config)
   if result:
      print 'ok'
   else:
      print 'failed'
      error(msg)

# ------------------------------------------------------------------------------
def cert_create(config, cn):
   type = opt.create
   cn   = pki.util.strip_invalid(cn)
   if cn:
      info('Creating ' + type + ' certificate with CN ' + cn + ': ')
      result, msg = pki.cmd.create_cert(config, cn, type)
      if result:
         print 'ok (serial: ' + pki.util.serial_from_cn(config, cn) + ')'
      else:
         print 'failed'
         error(msg)
   else:
      error('invalid CN given')

# ------------------------------------------------------------------------------
def cert_renew(config, cn):
   type = opt.renew
   cn   = pki.util.strip_invalid(cn)
   if cn:
      serial = pki.util.serial_from_cn(config, cn)
      if serial:
         info('Renewing ' + type + ' certificate with CN ' + cn + ': ')
         result, msg = pki.cmd.renew_cert(config, cn, opt.renew)
         if result:
            print ' ok (new serial: ' + pki.util.serial_from_cn(config,cn) + ')'
         else:
            print ' failed'
            error(msg)
      else:
         error('no serial found for ' + cn)
   else:
      error('invalid CN given')

# ------------------------------------------------------------------------------
def cert_revoke(config, cn):
   cn = pki.util.strip_invalid(cn)
   if cn:
      serial = pki.util.serial_from_cn(config, cn)
      if serial:
         info('Revoking certificate with CN ' + cn + ', serial ' + serial +': ')
         result, msg = pki.cmd.revoke_cert(config, cn, opt.revoke)
         if result:
            print ' ok'
         else:
            print ' failed'
            error(msg)
      else:
         error('no serial found for ' + cn)
   else:
      error('invalid CN given')

## We're being called as a script ##############################################
if __name__ == '__main__':
   opt, cn = parse_argv(sys.argv[1:])
   config  = pki.util.parse_config()
   if not config:
      error('unable to read/validate configuration')
   if opt.init:
      pki_init(config)
   else:
      if not pki.cmd.check_pki(config):
         error('PKI infrastructure not valid (first run with --init)')
      if opt.list:
         pki.cmd.list_certs(config, opt.list)
      elif opt.create:
         cert_create(config, cn)
      elif opt.renew:
         cert_renew(config, cn)
      elif opt.revoke:
         cert_revoke(config, cn)
