#!/bin/bash

## Revision history ############################################################
# author  : Wouter Eerdekens <info@fks.be>
# date    : 2011-08-12
# version : 0.1
# history : 2011-08-12 - Prepare for initial release <jeroen.hooyberghs@fks.be>
#           2006-07-26 - initial version.
################################################################################

## Read configuration.
[ ! -f /etc/vinty/scripts.conf ] && echo "error: cannot read config" && exit 1
. /etc/vinty/scripts.conf

## Read commandline arguments
CRL="$1"
[ ! -f "$CRL" ] && echo "error: cannot read CRL from $CRL" && exit 1

## Publish the CRL
if [ -z "$SSH_SERVER" ]
then
   if [ -n "$COPY_USER" && "$(id -un)" != "$COPY_USER" ]
   then
      sudo -u "$COPY_USER" "$0" "$CRL"
      RV=$?
   else
      if cp "$CRL" "$OPENVPN_DIR"
      then
         $OPENVPN_CMD
         RV=$?
      else
         RV=1
      fi
   fi
else
   if scp -P "$SSH_SERVER_PORT" -i "$SSH_SERVER_KEY" \
      "$KEY_DIR/$CRL" "$SSH_SERVER_LOGIN@$SSH_SERVER:$OPENVPN_DIR"
   then
      ssh -p "$SSH_SERVER_PORT" -i "$SSH_SERVER_KEY" \
          "$SSH_SERVER_LOGIN@$SSH_SERVER" $OPENVPN_CMD
      RV=$?
   else
      RV=1
   fi
fi
exit $RV
