FROM ubuntu:16.04
MAINTAINER oldiy <oldiy2018@gmail.com>

ENV VERSION 2.18

RUN apt-get update  && \
	apt-get install calibre python-pip unzip supervisor sqlite3 git bash -y  && \
	pip install jinja2 social-auth-app-tornado social-auth-storage-sqlalchemy tornado Baidubaike  && \
	mkdir -p /databak/  && \
	mkdir -p /data/log/  && \
	mkdir -p /data/books/  && \
	mkdir -p /data/release/www/calibre.talebook.org/  && \
	mkdir /data/books/{library,extract,upload,convert,progress}  && \
	cd /data/release/www/calibre.talebook.org/  && \
	git clone https://github.com/oldiy/my-calibre-webserver.git  && \
	#添加至少24本书后创建书库
	calibredb add --library-path=/data/books/library/  -r  /data/release/www/calibre.talebook.org/my-calibre-webserver/conf/book/  && \
	#创建数据库
	python /data/release/www/calibre.talebook.org/my-calibre-webserver/server.py --syncdb  && \
	#修改user_handlers.py为单机版
	sed -i 's/#"auto_login"    : 1,/"auto_login"    : 1,/g' /data/release/www/calibre.talebook.org/my-calibre-webserver/webserver/settings.py  && \
	cp /data/release/www/calibre.talebook.org/my-calibre-webserver/conf/supervisor/calibre-webserver.conf /etc/supervisor/conf.d/  && \
	#备份
	cp -rf /data/* /databak/  && \
	chmod +x /databak/release/www/calibre.talebook.org/my-calibre-webserver/start.sh  && \
	/usr/bin/supervisord

EXPOSE 8000

VOLUME ["/data"]

CMD ["/databak/release/www/calibre.talebook.org/my-calibre-webserver/start.sh"]
