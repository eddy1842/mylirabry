#!/bin/sh
if [ ! -f /var/www/html/conf/config.ini ]; then
	cp /conf-copy/config.ini /var/www/html/conf/config.ini
fi

ln -s /var/www/html/conf/config.ini /var/www/html/config.ini

docker-php-entrypoint apache2-foreground
