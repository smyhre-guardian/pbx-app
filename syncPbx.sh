#!/bin/bash

PBX="$1"

case "$PBX" in
    "SVRPBX02")
        cp /etc/asterisk/avaya_x.conf /etc/asterisk/avaya_x.conf.bak-$(date +%Y%m%d%H%M%S)
        cp /etc/asterisk/avaya_x.conf.pending /etc/asterisk/avaya_x.conf
        ;;
    "SVRPBX01")
        scp /etc/asterisk/avaya_x.conf.pending SVRPBX01:/etc/asterisk/avaya_x.conf.pending
        ssh SVRPBX01 "cp /etc/asterisk/avaya_x.conf /etc/asterisk/avaya_x.conf.bak-$(date +%Y%m%d%H%M%S) && cp /etc/asterisk/avaya_x.conf.pending /etc/asterisk/avaya_x.conf"
        ;;
    *)
        echo "Usage: $0 {SVRPBX01|SVRPBX02}"
        exit 1
        ;;
esac