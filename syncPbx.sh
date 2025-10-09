#!/bin/bash

PBX="$1"

case "$PBX" in
    "SVRPBX02")
        cp /etc/asterisk/avaya_x.conf /etc/asterisk/avaya_x.conf.bak-$(date +%Y%m%d%H%M%S)
        cp /etc/asterisk/avaya_x.conf.pending /etc/asterisk/avaya_x.conf
        ALINT_IGNORE=W_WSH_EOL,H_WSV_VARSET_BETWEEN /home/guardian/pbx-app/.v/bin/asterisklint dialplan-check /etc/asterisk/extensions.conf || { echo "lint failed"; exit 1; }
        ;;
    "SVRPBX01")
        scp /etc/asterisk/avaya_x.conf.pending 192.168.1.105:/etc/asterisk/avaya_x.conf.pending
        ssh 192.168.1.105 "cp /etc/asterisk/avaya_x.conf /etc/asterisk/avaya_x.conf.bak-$(date +%Y%m%d%H%M%S) && cp /etc/asterisk/avaya_x.conf.pending /etc/asterisk/avaya_x.conf"
        # ssh 192.168.1.105 "ALINT_IGNORE=W_WSH_EOL,H_WSV_VARSET_BETWEEN asterisklint dialplan-check /etc/asterisk/extensions.conf" || { echo "lint failed"; exit 1; }
        ;;
    *)
        echo "Usage: $0 {SVRPBX01|SVRPBX02}"
        exit 1
        ;;
esac