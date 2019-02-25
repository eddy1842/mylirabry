#!/bin/sh
if [ ! -d "/data/release/www" ]; then
  cp /databak/release/www/* /data/release/www/
fi
if [ ! -d "/data/books/convert" ]; then
  cp /databak/books/* /data/books/
fi
if [ ! -d "/data/log" ]; then
  cp /databak/log/* /data/log/
fi
supervisorctl reload all
