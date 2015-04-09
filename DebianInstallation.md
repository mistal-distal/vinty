# Introduction #

This page is made to describe the installation of vinty with the webinterface on a debian 6.0 installation


# Installation #

  * apt-get install git
  * git clone http://code.google.com/p/vinty/
  * cd vinty
  * make
  * (as root) make install
  * apt-get install apache2
  * add line to /etc/apache2/sites-enabled/000-default
> ` Include /etc/vinty/apache.conf `
  * add basic authentication if you want by editing /etc/vinty/apache.conf (htpasswd)
  * review settings in /etc/vinty/vinty.cfg, most importantly your ssl settings
  * /etc/init.d/apache2 restart
  * Open a browser to http://localhost/vinty

# First use #
  * "Vinty PKI Initialisation" screen appears, select initialise to start the basic install of needed CA + diffie hellman file. This could take a few minutes to complete, do not refresh or close the browser at this point.
  * You now entered the default screen in which you can create/revoke and download client and server certicates. You can also check logfiles if present, and secure your certificates with passwords.