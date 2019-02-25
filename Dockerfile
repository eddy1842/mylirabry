FROM ubuntu:16.04
MAINTAINER oldiy <oldiy2018@gmail.com>

RUN apt-get update  && \
	apt-get install calibre python-pip unzip supervisor sqlite3 git -y  && \
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
	python /data/release/www/calibre.talebook.org/my-calibre-webserver/server.py --syncdb  && \
	cp /data/release/www/calibre.talebook.org/my-calibre-webserver/conf/supervisor/calibre-webserver.conf /etc/supervisor/conf.d/  && \
	cp -rf /data/* /databak/  && \
	chmod +x /databak/release/www/calibre.talebook.org/my-calibre-webserver/start.sh  && \
	#/usr/bin/supervisord

RUN apt-get install bash -y

EXPOSE 8000

VOLUME ["/data"]

CMD ["/databak/release/www/calibre.talebook.org/my-calibre-webserver/start.sh"]
