#!/bin/sh
if [ ! -d "/data/release" ]; then
  cp /databak/* /data/
fi
supervisorctl reload all
