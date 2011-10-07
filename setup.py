#!/usr/bin/python

from distutils.core import setup

setup (
   version      = '0.1',
   description  = 'Vinty Public Key Infrastructure tools',
   author       = 'Wouter Eerdekens',
   author_email = 'info@fks.be',
   url          = 'http://www.fks.be/',
   packages     = ['pki'],
   package_dir  = { 'pki' : 'packages/pki' }
)
