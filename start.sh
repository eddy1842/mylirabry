#!/bin/sh
if [ ! -d "/data/release" ]; then
  cp -rf /databak/* /data/
fi
/usr/bin/supervisord
supervisorctl reload all