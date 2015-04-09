# Example sudo config. #
```
Cmnd_Alias      OPENVPN_RESTART = /etc/init.d/openvpn
Cmnd_Alias      OPENVPN_PUBLISH_CRL = /usr/share/vinty/scripts/publish_crl.sh
www-data        ALL=(root) NOPASSWD: OPENVPN_RESTART,OPENVPN_PUBLISH_CRL
```