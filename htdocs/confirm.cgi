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
import cgi, cgitb
import pki.cgi, pki.util

## We're being called as a script ##############################################
if __name__ == '__main__':
   cgitb.enable()
   form = cgi.FieldStorage()

   if form.has_key('action') and form.has_key('cn'):
      action = form['action'].value
      cn     = pki.util.strip_invalid(form['cn'].value)
      if cn:
         pki.cgi.start_html('Confirm: ' + action + ' certificate ' + cn)
         pki.cgi.show_confirm(action, cn)
         pki.cgi.end_html()
      else:
         pki.cgi.start_html('Invalid common name', True)
         pki.cgi.show_error('Please specify a valid common name.')
         pki.cgi.show_link('Go Back')
         pki.cgi.end_html()
   else:
      pki.cgi.start_html('Invalid call', True)
      pki.cgi.show_error('You cannot run this script directly.')
      pki.cgi.show_link('Go Back')
      pki.cgi.end_html()
