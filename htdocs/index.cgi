#!/usr/bin/python

## Revision history ############################################################
__author__  = 'Wouter Eerdekens <info@fks.be>'
__date__    = '2011-08-12'
__version__ = '0.1'
__history__ = """
2011-08-12 - Prepare for initial release <jeroen.hooyberghs@fks.be>
2006-07-26 - initial version.
"""
## Imports #####################################################################
import cgitb
import os
from os import path
import pki.util, pki.cmd, pki.cgi

## We're being called as a script ##############################################
if __name__ == '__main__':
   cgitb.enable()
   config = pki.util.parse_config()
   if not config:
      pki.cgi.start_html('Error parsing configuration', True)
      pki.cgi.show_error('There was an error parsing vinty' \
                         +' configuration. Please check your setup.')
      pki.cgi.end_html()
   else:
      if not pki.cmd.check_pki(config):
         pki.cgi.start_html('Vinty PKI Initialisation')
         pki.cgi.init_page()
         pki.cgi.end_html()
      else:
         pki.cgi.start_html('Vinty PKI Web Frontend')
         pki.cgi.main_page(config)
         pki.cgi.end_html()
