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
import pki
import pki.cmd
import pki.util
import os

## Functions ###################################################################
def start_html(title, error = False):
   print """Content-Type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
   <head>
      <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
      <link rel="stylesheet" href="vinty.css" type="text/css"/>
      <title>%(title)s</title>
   </head>
   <body>""" % { 'title' : title }
   if error:
      print '<h1 class="error">' + title + '</h1>'
   else:
      print '<h1>' + title + '</h1>'

# ------------------------------------------------------------------------------
def end_html():
   print """
   </body>
</html>"""

# ------------------------------------------------------------------------------
def show_link(text):
   print """
      <div class="footer">
         <form action="index.cgi" method="post">
            <input type="submit" value="%(text)s"/>
         </form>
      </div>
      """ % { 'text' : text }

# ------------------------------------------------------------------------------
def show_info(msg):
   print '<div class="info">' + msg + '</div>'

# ------------------------------------------------------------------------------
def show_cert_info(info):
   print '<div class="container">'
   for name, value in info:
      print """
         <div class="infotable">
            <span class="name">%(name)s:</span>
            <span class="value">%(value)s</span>
         </div>""" % { 'name' : name, 'value': value }
   print '</div>'

# ------------------------------------------------------------------------------
def show_error(msg):
   print """
      <div class="error">
         <pre>%(msg)s</pre>
      </div>
      """ % { 'msg' : msg }

# ------------------------------------------------------------------------------
def show_confirm(action, cn, type = None):
   print """
      <div class="info">
         Are you sure you want to %(action)s certificate %(cn)s?
      </div>
      <div class="footer">
         <form action="submit.cgi" method="post">
            <input type="hidden" name="action" value="%(action)s"/>
            <input type="hidden" name="cn" value="%(cn)s"/>
            <input type="submit" value="Yes"/>
         </form>
         <form action="index.cgi" method="post">
            <input type="submit" value="No"/>
         </form>
      """ % { 'action' : action, 'cn' : cn }

# ------------------------------------------------------------------------------
def init_page():
   print """
      <div class="info">
         <p>
            This seems to be a new installation, so the root Certificate
            Authority and a Certificate Revocation List need to be created.
         </p><p>
            This might take a long time to complete. Do not interrupt or reload
            this page.
         </p><p>
            Click <tt>Initialise</tt> to start the
            initialisation process.
         </p>
      </div>
      <div class="footer">
         <form action="init.cgi" method="post">
            <input type="submit" value="Initialise" class="button"/>
         </form>
      </div>
      """

# ------------------------------------------------------------------------------
def main_page(config):
   list = []
   map(list.append,map(lambda x: x[3], pki.cmd.list_certs(config,'valid',True)))
   list.sort()
   cert_create(config.get('keys','size'))
   cert_download(list)
   cert_renew(list)
   cert_revoke(list)
   cert_passwd(list)
   cert_misc()

# ------------------------------------------------------------------------------
def cn_as_option(text):
   print '<option name="%(text)s">%(text)s</option>' % { 'text' : text }

# ------------------------------------------------------------------------------
def cert_create(keysize):
   print """
      <div class="container">
         <h2>Create certificate/key pairs</h2>
         <form action="submit.cgi" method="post">
            <div class="table">
               <span class="name">Key size:</span>
               <span class="value">%(keysize)s bit</span>
            </div>
            <div class="table">
               <span class="name">Common name:</span>
               <span class="value">
                  <input type="text" name="cn" size="20"/>
               </span>
            </div>
            <div class="table">
               <span class="name">Type:</span>
               <span class="value">
                  <select name="type">
                     <option value="client">client</option>
                     <option value="server">server</option>
                  </select>
                  certificate
               </span>
            </div>
            <input type="submit" value="Create" class="button"/>
            <input type="hidden" name="action" value="create"/>
         </form>
      </div>
      """ % { 'keysize' : keysize }

# ------------------------------------------------------------------------------
def cert_download(list):
   print """
      <div class="container">
         <h2>Download certificate/key pairs</h2>
         <form action="submit.cgi" method="get">
            <div class="table">
               <span class="name">Common name:</span>
               <span class="value">
                  <select name="cn" class="cn">
      """
   map(lambda x: cn_as_option(x), list)
   print """
                  </select>
                  <input type="submit" value="Download" class="button"/>
               </span>
            </div>
            <input type="hidden" name="action" value="download"/>
         </form>
      """

# ------------------------------------------------------------------------------
def cert_renew(list):
   print """
         <h2>Renew certificates</h2>
         <form action="confirm.cgi" method="post">
            <div class="table">
               <span class="name">Common name:</span>
               <span class="value">
                  <select name="cn" class="cn">
      """
   map(lambda x: cn_as_option(x), list)
   print """
                  </select>
                  <input type="submit" value="Renew" class="button"/>
               </span>
            </div>
            <input type="hidden" name="action" value="renew"/>
         </form>
      """

# ------------------------------------------------------------------------------
def cert_revoke(list):
   print """
         <h2>Revoke certificates</h2>
         <form action="confirm.cgi" method="post">
            <div class="table">
               <span class="name">Common name:</span>
               <span class="value">
                  <select name="cn" class="cn">
      """
   map(lambda x: cn_as_option(x), list)
   print """
                  </select>
                  <input type="submit" value="Revoke" class="button"/>
               </span>
            </div>
            <input type="hidden" name="action" value="revoke"/>
         </form>
      </div>
      """

# ------------------------------------------------------------------------------
def cert_passwd(list):
   print """
      <div class="container">
         <h2>Key certificate password</h2>
         <form action="submit.cgi" method="post">
            <div class="table">
               <span class="name">Common name:</span>
               <span class="value">
                  <select name="cn" class="cn">
      """
   map(lambda x: cn_as_option(x), list)
   print """
                  </select>
                  <input type="submit" value="Add/Remove Password" class="button"/>
                  <input type="radio" name="action" value="p_add" checked="true" /> Add
                  <input type="radio" name="action" value="p_remove" /> Remove
               </span>
               <span class="value">(Old/New) Password:
                  <input type="text" name="password" size="20"/>
               </span>
            </div>
         </form>
      </div>
      """

# ------------------------------------------------------------------------------
def cert_misc():
   print """
      <div class="container">
         <h2>Miscellaneous</h2>
         <div class="table">
            <span class="name">Certificate Revocation List</span>
            <span class="value">
               <form action="submit.cgi" method="post">
                  <input type="hidden" name="action" value="publish"/>
                  <input type="submit" value="Publish" class="button"/>
               </form>
            </span>
         </div>
         <div class="table">
            <span class="name">Certificate Database</span>
            <span class="value">
               <form action="submit.cgi" method="post">
                  <input type="hidden" name="action" value="show"/>
                  <input type="submit" value="Show" class="button"/>
               </form>
            </span>
         </div>
	<div class="table">
            <span class="name">Active Connections</span>
            <span class="value">
               <form action="submit.cgi" method="post">
                  <input type="hidden" name="action" value="con_show"/>
                  <input type="submit" value="Show" class="button"/>
               </form>
            </span>
         </div>
        <div class="table">
            <span class="name">Openvpn logfile</span>
            <span class="value">
               <form action="submit.cgi" method="post">
                  <input type="hidden" name="action" value="log_show"/>
                  <input type="submit" value="Show" class="button"/>
               </form>
            </span>
         </div>
      </div>
      """

# ------------------------------------------------------------------------------
def show_cert_db(config):
   keyDir = config.get('keys', 'path')
   list = pki.cmd.list_certs(config, 'all', True)
   print """
      <table>
         <tr>
            <th>Serial</th>
            <th>Common name</th>
            <th>Certificate type</th>
            <th>Status</th>
            <th>Valid until</th>
            <th>Date revoked</th>
            <th>With Password</th>
         </tr>
      """
   for status, serial, date, cn, type in list:
      print '<tr>'
      print '<td>' + serial + '</td>'
      print '<td>' + cn + '</td>'
      print '<td>' + type + '</td>'
      if status == pki.CERT_VALID:
         print '<td>Valid</td>'
         print '<td>' + date + '</td>'
         print '<td></td>'
      if status == pki.CERT_REVOKED:
         print '<td>Revoked</td>'
         print '<td></td>'
         print '<td>' + date + '</td>'
      if status == pki.CERT_EXPIRED:
         print '<td>Expired</td>'
         print '<td>' + date + '</td>'
         print '<td></td>'
      if status == pki.CERT_VALID:
         print '<td>' + str(pki.util.is_encrypted(os.path.join(keyDir,cn+'.key'))) + '</td>'
      else:
         print '<td></td>'
      print '</tr>'
   print '</table>'

# ------------------------------------------------------------------------------
def show_con_file(config):
   print """
      <table>
         <tr>
           <td>
     """
#   os.execv('/bin/cat', ['/etc/openvpn/openvpn-status.log'])
   file = open('/etc/openvpn/openvpn-status.log')
   lines = file.readlines()
   for line in lines :
      print line 
      print '<br />'
   print """	
           </td>
         </tr>
      """
   print '</table>'

# ------------------------------------------------------------------------------
def show_log_file(config):
   print """
      <table>
         <tr>
           <td>
     """
#   os.execv('/bin/cat', ['/etc/openvpn/openvpn-status.log'])
   fileName = config.get('log','file')
   if fileName == None : fileName = '/var/log/openvpn.log'
   nNeeded = int(config.get('log','nLines'))
   if nNeeded == None : nNeeded = 200
   try :
      # count number of lines in file
      nLines = 0
      file = open(fileName)
      if file != None :
         block = file.readlines(32000) # read nearly 32kbytes
         if len(block) != 0 :
            while len(block) != 0 :
               nLines += len(block)
               block = file.readlines(32000) # read nearly 32kbytes
            # skip (nLines - nNeeded) lines
            nLinesToBeSkipped = nLines - nNeeded
            if nLinesToBeSkipped < 0 :
               nLinesToBeSkipped = 0
            file.seek(0)
            nLinesSkipped = 0
            nLinesRead = 0
            while nLinesRead <= nLinesToBeSkipped :
               nLinesSkipped = nLinesRead
               block = file.readlines(32000) # read nearly 32kbytes
               nLinesRead += len(block)
            # first line to print is in 'block'
            firstOne = nLinesToBeSkipped - nLinesSkipped
            while len(block) != 0 :
               i = firstOne
               while i < len(block) :
                  # print single line
                  print block[i].rstrip()
                  i += 1
                  print '<br />'
               block = file.readlines(32000) # read nearly 32kbytes
               firstOne = 0
      else :
         print 'No file ' + fileName
   except IOError, ioe :
      print ioe
      print 'Unable to read file ' + fileName
   else :
      print """	
              </td>
            </tr>
         """
      print '</table>'
