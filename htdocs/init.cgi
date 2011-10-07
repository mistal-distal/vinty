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
      pki.cgi.show_error('There was an error parsing the vinty' \
                         + ' configuration. Please check your setup.')
      pki.cgi.end_html()
   else:
      if pki.cmd.check_pki(config):
         pki.cgi.start_html('VInty PKI already initialised', True)
         pki.cgi.show_error('The vinty PKI structure is already initialised.' \
                            ' Remove the previous installation first.')
         pki.cgi.show_link('OK')
         pki.cgi.end_html()
      else:
         result, msg = pki.cmd.create_pki(config)
         if result:
            pki.cgi.start_html('Vinty PKI initialisation complete')
            pki.cgi.show_info('You can now start using the Vinty Web Frontend.')
            pki.cgi.show_link('OK')
            pki.cgi.end_html()
         else:
            pki.cgi.start_html('Vinty PKI initialisation failed', True)
            pki.cgi.show_error(msg)
            pki.cgi.show_link('Go Back')
            pki.cgi.end_html()
