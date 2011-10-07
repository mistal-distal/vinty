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
import commands, os, re, sets, stat, string, sys, tempfile, zipfile
import pki
from ConfigParser import ConfigParser
from os import path

## Functions ###################################################################
def parse_config():
   configFile = '/etc/vinty/vinty.cfg'
   try:
      cp = ConfigParser()
      cp.readfp(open(configFile))
   except:
      cp = None
   else:
      if not test_config(cp):
         cp = None 
   return cp

# ------------------------------------------------------------------------------
def test_config(config):
   # -- Dictionary containing expected configuration sections and options
   cfg = { 'openssl' : ('path', 'conf'),
           'keys'    : ('path', 'path_revoked', 'size', 'expire', 'country',
                        'province', 'city', 'org', 'ou', 'email'),
           'ca'      : ('name', 'expire', 'crl')
         }
   
   rv = True
   for section in cfg.keys():
      if not config.has_section(section):
         rv = False
      else:
         for option in cfg[section]:
            if not config.has_option(section, option):
               rv = False
            elif not config.get(section,option) and option != 'ou':
               rv = False
   return rv

# ------------------------------------------------------------------------------
def check_permissions(file):
   if path.isfile(file) \
      and oct(os.stat(file)[stat.ST_MODE] & 0777) in ('0400','0600'):
      rv = True
   else:
      rv = False
   return rv

# ------------------------------------------------------------------------------
def is_private_key(file):
   if path.isfile(file):
      exp    = re.compile('BEGIN RSA PRIVATE KEY', re.MULTILINE)
      result = exp.search(open(file).read())
      if result:
         rv = True
      else:
         rv = False
   else:
      rv = False
   return rv

# ------------------------------------------------------------------------------
def is_encrypted(file):
   if path.isfile(file):
      exp    = re.compile('^Proc-Type: 4,ENCRYPTED', re.MULTILINE)
      result = exp.search(open(file).read())
      if result:
         rv = True
      else:
         rv = False
   else:
      rv = False
   return rv

# ------------------------------------------------------------------------------
def strip_invalid(cn):
   all   = ''.join(map(chr, range(256)))
   valid = string.lowercase + string.digits + '._-'
   valid = ''.join(sets.Set(all).difference(valid))
   cn    = cn.lower().translate(all, valid)
   return cn

# ------------------------------------------------------------------------------
def move_revoked(config, filelist, serial):
   destDir = path.join(config.get('keys', 'path_revoked'), serial)
   try:
      os.makedirs(destDir, 0700)
      for file in filelist:
         dest = path.join(destDir, os.path.basename(file))
         os.rename(file, dest)
   except:
      rv = False
   else:
      rv = True
   return rv

# ------------------------------------------------------------------------------
def serial_from_cn(config, cn):
   serial  = None
   keyDir  = config.get('keys', 'path')
   crtFile = path.join(keyDir, cn + '.crt')
   if path.isfile(crtFile):
      exp = re.compile('(^.*Serial Number:)(.*[0-9]+.*)(\(.*\)$)', re.MULTILINE)
      result = exp.search(open(crtFile).read())
      if result and len(result.groups()) == 3:
         serial = hex(int(result.group(2).strip()))[2:].upper()
         if len(serial) % 2:
            serial = '0' + serial
   return serial

# ------------------------------------------------------------------------------
def cert_type(config, serial, status):
   if status == pki.CERT_VALID:
      keyDir  = config.get('keys', 'path')
      pemFile = path.join(keyDir, serial + '.pem')
   else:
      revDir  = config.get('keys', 'path_revoked')
      pemFile = path.join(path.join(revDir, serial), serial + '.pem')
   if path.isfile(pemFile):
      exp = re.compile('.*SSL Server$', re.MULTILINE)
      result = exp.search(open(pemFile).read())
      if result:
         rv = pki.CERT_SERVER
      else:
         rv = pki.CERT_CLIENT
   else:
      rv = None
   return rv

# ------------------------------------------------------------------------------
def cert_files(config, cn, serial, download = False):
   keyDir = config.get('keys', 'path')
   files  = []
   rv     = None
   if serial:
      if download:
         files.append(path.join(keyDir, cn + '.crt'))
         files.append(path.join(keyDir, cn + '.key'))
         files.append(path.join(keyDir, config.get('ca', 'name') + '.crt'))
         if cert_type(config, serial, pki.CERT_VALID) == pki.CERT_SERVER:
            keySize = config.get('keys', 'size')
            files.append(path.join(keyDir, 'dh' + keySize + '.pem'))
      else:
         files.append(path.join(keyDir, cn + '.csr'))
         files.append(path.join(keyDir, cn + '.crt'))
         files.append(path.join(keyDir, cn + '.key'))
         files.append(path.join(keyDir, serial + '.pem'))
      for file in files:
         if not path.isfile(file):
            break
      else:
            rv = files
   return rv

# ------------------------------------------------------------------------------
def create_ssl_script(config, cn = ''):
   try:
      fd, fname = tempfile.mkstemp()
      os.write(fd, """#!/bin/bash
export KEY_DIR="%(dir)s"
export KEY_CN="%(cn)s"
export KEY_SIZE="%(size)s"
export KEY_EXPIRE="%(expire)s"
export KEY_COUNTRY="%(country)s"
export KEY_PROVINCE="%(province)s"
export KEY_CITY="%(city)s"
export KEY_ORG="%(org)s"
export KEY_OU="%(ou)s"
export KEY_EMAIL="%(email)s"
""" % { 'dir'      : config.get('keys', 'path'),
        'cn'       : cn,
        'size'     : config.get('keys', 'size'),
        'expire'   : config.get('keys', 'expire'),
        'country'  : config.get('keys', 'country'),
        'province' : config.get('keys', 'province'),
        'city'     : config.get('keys', 'city'),
        'org'      : config.get('keys', 'org'),
        'ou'       : config.get('keys', 'ou'),
        'email'    : config.get('keys', 'email')
      })
   except:
      fd    = None
      fname = None
   return fd, fname

# ------------------------------------------------------------------------------
def run_ssl_script(script):
   os.chmod(script, 0700)
   status, output = commands.getstatusoutput(script)
   os.remove(script)
   return not status, output
