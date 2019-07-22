#!/usr/bin/python
#-*- coding: UTF-8 -*-

import logging
import douban
import baike
import subprocess
from base_handlers import *

from settings import settings
from calibre.ebooks.metadata import authors_to_string
from calibre.ebooks.conversion.plumber import Plumber
from calibre.customize.conversion import OptionRecommendation, DummyReporter

BOOKNAV = (
(
u"文學", (
u"小說", u"外國文學", u"文學", u"隨筆", u"中國文學", u"經典", u"散文", u"日本文學", u"村上春樹",
u"童話", u"詩歌", u"王小波", u"雜文", u"張愛玲", u"兒童文學", u"余華", u"古典文學", u"名著",
u"錢鐘書", u"當代文學", u"魯迅", u"外國名著", u"詩詞", u"茨威格", u"杜拉斯", u"米蘭·昆德拉", u"港台",
)
),

        (
u"流行", (
u"漫畫", u"繪本", u"推理", u"青春", u"言情", u"科幻", u"韓寒", u"武俠", u"懸疑",
u"耽美", u"亦舒", u"東野圭吾", u"日本漫畫", u"奇幻", u"安妮寶貝", u"三毛", u"郭敬明", u"網絡小說",
u"穿越", u"金庸", u"幾米", u"輕小說", u"推理小說", u"阿加莎·克里斯蒂", u"張小嫻", u"幾米",
u"魔幻", u"青春文學", u"高木直子", u"J.K.羅琳", u"滄月", u"落落", u"張悅然", u"古龍", u"科幻小說",
u"蔡康永",
)
),

        (
u"文化", (
u"歷史", u"心理學", u"哲學", u"傳記", u"文化", u"社會學", u"設計", u"藝術", u"政治",
u"社會", u"建築", u"宗教", u"電影", u"數學", u"政治學", u"回憶錄", u"思想", u"國學",
u"中國歷史", u"音樂", u"人文", u"戲劇", u"人物傳記", u"繪畫", u"藝術史", u"佛教", u"軍事",
u"西方哲學", u"二戰", u"自由主義", u"近代史", u"考古", u"美術",
)
),

        (
u"生活", (
u"愛情", u"旅行", u"生活", u"勵志", u"成長", u"攝影", u"心理", u"女性",
u"職場", u"美食", u"遊記", u"教育", u"靈修", u"情感", u"健康", u"手工",
u"養生", u"兩性", u"家居", u"人際關係", u"自助游",
)
),

        (
u"經管", (
u"經濟學", u"管理", u"經濟", u"金融", u"商業", u"投資", u"營銷", u"理財",
u"創業", u"廣告", u"股票", u"企業史", u"策劃",
)
),

        (
u"科技", (
u"科普", u"互聯網", u"編程", u"科學", u"交互設計", u"用戶體驗",
u"算法", u"web", u"科技", u"UE", u"UCD", u"通信", u"交互",
u"神經網絡", u"程序",
),

),
)

import Queue, threading, functools
_q = Queue.Queue()

def background(func):
    @functools.wraps(func)
    def run(*args, **kwargs):
        def worker():
            try:
                func(*args, **kwargs)
            except:
                import traceback, logging
                logging.error('Failed to run background task:')
                logging.error(traceback.format_exc())

        t = threading.Thread(name='worker', target=worker)
        t.setDaemon(True)
        t.start()
    return run

def do_ebook_convert(old_path, new_path, log_path):
    '''convert book, and block, and wait'''
    args = ['ebook-convert', old_path, new_path]
    if new_path.lower().endswith(".epub"): args += ['--flow-size', '0']

    log = open(log_path, "w", 0)
    p = subprocess.Popen(args, stdout=log, stderr=subprocess.PIPE)
    err = ""
    while p.poll() == None:
        _, e = p.communicate()
        err += e
    logging.info("ebook-convert finish: %s" % new_path)

    if err:
        log.write(err)
        log.write(u"\n服務器處理異常，請聯繫管理員。\n[FINISH]")
        log.close()
        return (False, err)
    return (True, "")


class Index(BaseHandler):
    def get(self):
        import random
        nav = "index"
        title = _(u'全部書籍')
        ids = list(self.cache.search(''))
        if not ids: raise web.HTTPError(404, reason = _(u'本書庫暫無藏書'))
        random_ids = random.sample(ids, min(8*3, len(ids)))
        random_books = [ b for b in self.get_books(ids=random_ids) if b['cover'] ][:8]
        ids.sort()
        new_ids = random.sample(ids[-300:], min(20, len(ids)))
        new_books = [ b for b in self.get_books(ids=new_ids) if b['cover'] ][:10]
        return self.html_page('index.html', vars())

class About(BaseHandler):
    def get(self):
        nav = "about"
        return self.html_page('about.html', vars())

class BookDetail(BaseHandler):
    def get(self, id):
        book = self.get_book(id)
        book_id = book['id']
        book['is_owner'] = self.is_book_owner(book_id, self.user_id())
        book['is_public'] = True
        if ( book['publisher'] and book['publisher'] in (u'中信出版社') ) or u'吳曉波' in list(book['authors']):
            if not book['is_owner']:
                book['is_public'] = False
        if self.is_admin():
            book['is_public'] = True
            book['is_owner'] = True
        self.user_history('visit_history', book)
        try: sizes = [ (f, self.db.sizeof_format(book_id, f, index_is_id=True)) for f in book['available_formats'] ]
        except: sizes = []
        title = book['title']
        smtp_username = settings['smtp_username']
        if self.user_id(): self.count_increase(book_id, count_visit=1)
        else: self.count_increase(book_id, count_guest=1)
        return self.html_page('book/detail.html', vars())

class BookRefer(BaseHandler):
    @web.authenticated
    def get(self, id):
        book_id = int(id)
        mi = self.db.get_metadata(book_id, index_is_id=True)
        title = re.sub(u'[(（].*', "", mi.title)

        api = douban.DoubanBookApi(settings['douban_apikey'], copy_image=False)
        # first, search title
        books = api.get_books_by_title(title)
        books = [] if books == None else books
        if books and mi.isbn and mi.isbn != baike.BAIKE_ISBN:
            if mi.isbn not in [ b.get('isbn13', "xxx") for b in books ]:
                book = api.get_book_by_isbn(mi.isbn)
                # alwayse put ISBN book in TOP1
                if book: books.insert(0, book)
        books = [ api._metadata(b) for b in books ]

        # append baidu book
        api = baike.BaiduBaikeApi(copy_image=False)
        book = api.get_book(title)
        if book: books.append( book )
        self.set_header("Cache-control", "no-cache")
        return self.html_page('book/refer.html', vars())


class BookReferSet(BaseHandler):
    @web.authenticated
    def post(self, id, isbn):
        book_id = int(id)
        if not isbn.isdigit():
            raise web.HTTPError(400, reason = _(u'ISBN參數錯誤') )
        mi = self.db.get_metadata(book_id, index_is_id=True)
        if not mi:
            raise web.HTTPError(404, reason = _(u'書籍不存在') )
        if not self.is_admin() and not self.is_book_owner(book_id, self.user_id()):
            raise web.HTTPError(403, reason = _(u'無權限'))

        title = re.sub(u'[(（].*', "", mi.title)
        if isbn == baike.BAIKE_ISBN:
            api = baike.BaiduBaikeApi(copy_image=True)
            refer_mi = api.get_book(title)
        else:
            mi.isbn = isbn
            api = douban.DoubanBookApi(settings['douban_apikey'], copy_image=True)
            refer_mi = api.get_book(mi)

        if mi.cover_data[0]:
            refer_mi.cover_data = None
        mi.smart_update(refer_mi, replace_metadata=True)
        self.db.set_metadata(book_id, mi)
        return self.redirect('/book/%d'%book_id)



class BookRating(BaseHandler):
    @json_response
    def post(self, id):
        rating = self.get_argument("rating", None)
        try:
            r = float(rating)
        except:
            return {'ecode': 2, 'msg': _(u"評星無效")}

        book_id = int(id)
        mi = self.db.get_metadata(book_id, index_is_id=True)
        mi.rating = r
        self.db.set_metadata(book_id, mi)
        if self.user_id(): self.count_increase(book_id, count_visit=1)
        else: self.count_increase(book_id, count_guest=1)
        return {'ecode': 0, 'msg': _(u'更新成功')}

class BookEdit(BaseHandler):
    @json_response
    def post(self, id):
        field = self.get_argument("field", None)
        content = self.get_argument("content", "").strip()
        if not field or not content:
            return {'ecode': 1, 'msg': _(u"參數錯誤")}

        book_id = int(id)
        mi = self.db.get_metadata(book_id, index_is_id=True)
        if field == 'pubdate':
            try:
                content = datetime.datetime.strptime(content, "%Y-%m-%d")
            except:
                return {'ecode': 2, 'msg': _(u"日期格式錯誤，應為 2018-05-10 這種格式")}
        elif field == 'authors':
            content = list(set([ v.strip() for v in content.split(";") if v.strip() ]))
            mi.set('author_sort', content[0])
        elif field == 'tags':
            content = content.replace(" ", "").split("/")
        mi.set(field, content)
        self.db.set_metadata(book_id, mi)
        return {'ecode': 0, 'msg': _(u"更新成功")}

class BookDelete(BaseHandler):
    def get(self, id):
        return self.post(id)

    @web.authenticated
    def post(self, id):
        book = self.get_book(id)
        book_id = book['id']
        cid = book['collector']['id']

        if self.is_admin() or self.is_book_owner(book_id, cid):
            self.db.delete_book( book_id )
            self.add_msg('success', _(u"刪除完畢"))
            self.redirect("/book")
        else:
            self.add_msg('danger', _(u"無權限操作"))
            self.redirect("/book/%s"%book_id)

class BookDownload(BaseHandler):
    @web.authenticated
    def get(self, id, fmt):
        fmt = fmt.lower()
        logging.debug("download %s.%s" % (id, fmt))
        book = self.get_book(id)
        book_id = book['id']
        self.user_history('download_history', book)
        self.count_increase(book_id, count_download=1)
        if 'fmt_%s'%fmt not in book:
            raise web.HTTPError(404, reason = _(u'%s格式無法下載'%(fmt)) )
        path = book['fmt_%s'%fmt]
        att = u'attachment; filename="%d-%s.%s"' % (book['id'], book['title'], fmt)
        self.set_header('Content-Disposition', att.encode('UTF-8'))
        self.set_header('Content-Type', 'application/octet-stream')
        f = open(path, 'rb').read()
        self.write( f )

class BookList(ListHandler):
    def get(self):
        title = _(u'全部書籍')
        category_name = 'books'
        tagmap = self.all_tags_with_count()
        navs = []
        for h1, tags in BOOKNAV:
            tags = list( (v, tagmap.get(v, 0)) for v in tags )
            #tags.sort( lambda x,y: cmp(y[1], x[1]) )
            navs.append( (h1, tags) )

        return self.html_page('book/all.html', vars())

class RecentBook(ListHandler):
    def get(self):
        title = _(u'新書推薦') % vars()
        category = "recents"
        ids = self.books_by_timestamp()
        return self.render_book_list([], vars(), ids=ids);

class SearchBook(ListHandler):
    def get(self):
        name = self.get_argument("name", "")
        if not name.strip():
            raise web.HTTPError(403, reason = _(u"請輸入搜索關鍵字") )

        title = _(u'搜索：%(name)s') % vars()
        ids = self.cache.search(name)
        books = self.get_books(ids=ids)
        search_query = name
        return self.render_book_list(books, vars());

class HotBook(ListHandler):
    def get(self):
        title = _(u'熱度榜單')
        db_items = self.session.query(Item).filter(Item.count_visit > 1 ).order_by(Item.count_download.desc())
        count = db_items.count()
        start = self.get_argument_start()
        delta = 20
        page_max = count / delta
        page_now = start / delta
        pages = []
        for p in range(page_now-4, page_now+4):
            if 0 <= p and p <= page_max:
                pages.append(p)
        items = db_items.limit(delta).offset(start).all()
        ids = [ item.book_id for item in items ]
        books = self.get_books(ids=ids)
        self.do_sort(books, 'count_visit', False)
        return self.html_page('book/list.html', vars())

class BookAdd(BaseHandler):
    @web.authenticated
    def get(self):
        title = _(u'添加書籍')
        return self.html_page('book/add.html', vars())


class BookUpload(BaseHandler):
    @web.authenticated
    def post(self):
        def convert(s):
            try: return s.group(0).encode('latin1').decode('utf8')
            except: return s.group(0)

        import re
        from calibre.ebooks.metadata import MetaInformation
        postfile = self.request.files['ebook_file'][0]
        name = postfile['filename']
        name = re.sub(r'[\x80-\xFF]+', convert, name)
        logging.error('upload book name = ' + repr(name))
        fmt = os.path.splitext(name)[1]
        fmt = fmt[1:] if fmt else None
        if not fmt:
            return "bad file name: %s" % name
        fmt = fmt.lower()

        # save file
        data = postfile['body']
        fpath = os.path.join(settings['upload_path'], name)
        with open(fpath, "wb") as f:
            f.write(data)

        # read ebook meta
        stream = open(fpath, 'rb')
        mi = get_metadata(stream, stream_type=fmt, use_libprs_metadata=True)
        if fmt.lower() == "txt":
            mi.title = name.replace(".txt", "")
            mi.authors = [_(u'佚名')]
        logging.info('upload mi.title = ' + repr(mi.title))
        books = self.db.books_with_same_title(mi)
        if books:
            book_id = books.pop()
            return self.redirect('/book/%d'%book_id)

        fpaths = [fpath]
        book_id = self.db.import_book(mi, fpaths )
        self.user_history('upload_history', {'id': book_id, 'title': mi.title})
        self.add_msg('success', _(u"導入書籍成功！"))
        item = Item()
        item.book_id = book_id
        item.collector_id = self.user_id()
        item.save()
        return self.redirect('/book/%d'%book_id)

class BookRead(BaseHandler):
    @web.authenticated
    def get(self, id):
        book = self.get_book(id)
        book_id = book['id']
        self.user_history('read_history', book)
        self.count_increase(book_id, count_download=1)

        # check format
        for fmt in ['epub', 'mobi', 'azw', 'azw3', 'txt']:
            fpath = book.get("fmt_%s" % fmt, None)
            if not fpath: continue
            # epub_dir is for javascript
            epub_dir = os.path.dirname(fpath).replace(settings['with_library'], "/extract/")
            self.extract_book(book, fpath, fmt)
            return self.html_page('book/read.html', vars())
        self.add_msg('success', _(u"抱歉，在線閱讀器暫不支持該格式的書籍"))
        self.redirect('/book/%d'%book_id)

    @background
    def extract_book(self, book, fpath, fmt):
        fdir = os.path.dirname(fpath).replace(settings['with_library'], settings['extract_path'])
        subprocess.call(['mkdir', '-p', fdir])
        #fdir = os.path.dirname(fpath) + "/extract"
        if os.path.isfile(fdir+"/META-INF/container.xml"):
            subprocess.call(["chmod", "a+rx", "-R", fdir + "/META-INF"])
            return

        progress_file = self.get_path_progress(book['id'])
        new_path = ""
        if fmt != "epub":
            new_fmt = "epub"
            new_path = os.path.join(settings["convert_path"], 'book-%s-%s.%s'%(book['id'], int(time.time()), new_fmt) )
            logging.error('convert book: %s => %s' % ( fpath, new_path));
            os.chdir('/tmp/')

            ok, err = do_ebook_convert(fpath, new_path, progress_file)
            if not ok:
                self.add_msg("danger", u'文件格式轉換失敗，請聯繫管理員.')
                return

            self.db.add_format(book['id'], new_fmt, open(new_path, "rb"), index_is_id=True)
            fpath = new_path

        # extract to dir
        logging.error('extract book: %s' % fpath)
        os.chdir(fdir)
        log = open(progress_file, "a")
        log.write(u"Dir: %s\n" % fdir)
        subprocess.call(["unzip", fpath, "-d", fdir], stdout=log)
        subprocess.call(["chmod", "a+rx", "-R", fdir+ "/META-INF"])
        if new_path: subprocess.call(["rm", new_path])
        log.close()
        return


class BookPush(BaseHandler):
    @web.authenticated
    def post(self, id):
        mail_to = self.get_argument("mail_to", None)
        if not mail_to:
            return self.redirect("/setting")

        book = self.get_book(id)
        book_id = book['id']

        self.user_history('push_history', book)
        self.count_increase(book_id, count_download=1)

        # check format
        for fmt in ['mobi', 'azw', 'pdf']:
            fpath = book.get("fmt_%s" % fmt, None)
            if fpath:
                self.do_send_mail(book, mail_to, fmt, fpath)
                self.add_msg( "success", _(u"服務器正在推送……"))
                return self.redirect("/book/%d"%book['id'])

        # we do no have formats for kindle
        if 'fmt_epub' not in book and 'fmt_azw3' not in book and 'fmt_txt' not in book:
            raise web.HTTPError(404, reason = _(u"抱歉，該書無可用於kindle閱讀的格式"))
        self.convert_book(book, mail_to)
        self.add_msg( "success", _(u"後台正在推送了~"))
        self.redirect("/book/%d"%book['id'])

    @background
    def convert_book(self, book, mail_to=None):
        new_fmt = 'mobi'
        new_path = os.path.join(settings['convert_path'], '%s.%s' % (ascii_filename(book['title']), new_fmt) )
        progress_file = self.get_path_progress(book['id'])

        old_path = None
        for f in ['txt', 'azw3', 'epub']: old_path = book.get('fmt_%s' %f, old_path)

        ok, err = do_ebook_convert(old_path, new_path, progress_file)
        if not ok:
            self.add_msg("danger", u'文件格式轉換失敗，請聯繫管理員.')
            return

        self.db.add_format(book['id'], new_fmt, open(new_path, "rb"), index_is_id=True)
        if mail_to:
            self.do_send_mail(book, mail_to, new_fmt, new_path)
        return

    @background
    def do_send_mail(self, book, mail_to, fmt, fpath):
        # read meta info
        author = authors_to_string(book['authors'] if book['authors'] else [_(u'佚名')])
        title = book['title'] if book['title'] else _(u"無名書籍")
        fname = u'%s - %s.%s'%(title, author, fmt)
        fdata = open(fpath).read()

        mail_from = settings['smtp_username']
        mail_subject = _('圖書管理系統：推送給您一本書《%(title)s》') % vars()
        mail_body = _(u'為您奉上一本《%(title)s》, 歡迎使用圖書管理系統' % vars())
        status = msg = ""
        try:
            logging.info('send %(title)s to %(mail_to)s' % vars())
            mail = self.create_mail(mail_from, mail_to, mail_subject,
                    mail_body, fdata, fname)
            sendmail(mail, from_=mail_from, to=[mail_to], timeout=30,
                    relay=settings['smtp_server'],
                    username=settings['smtp_username'],
                    password=settings['smtp_password']
                    )
            status = "success"
            msg = _('[%(title)s] 已成功發送至Kindle郵箱 [%(mail_to)s] !!') % vars()
            logging.info(msg)
        except:
            import traceback
            logging.error('Failed to send to kindle:')
            logging.error(traceback.format_exc())
            status = "danger"
            msg = traceback.format_exc()
        self.add_msg(status, msg)
        return

    def create_mail(self, sender, to, subject, body, attachment_data, attachment_name):
        from email.header import Header
        from email.utils import formatdate
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.application import MIMEApplication
        def get_md5(s):
            import hashlib
            md5 = hashlib.md5()
            md5.update(s)
            return md5.hexdigest()

        mail = MIMEMultipart()
        mail['From'] = sender
        mail['To'] = to
        mail['Subject'] = Header(subject, 'utf-8')
        mail['Date'] = formatdate(localtime=True)
        mail['Message-ID'] = '<tencent_%s@qq.com>' % get_md5(mail.as_string())
        mail.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        if body is not None:
            msg = MIMEText(body, 'plain', 'utf-8')
            mail.attach(msg)

        if attachment_data is not None:
            name = Header(attachment_name, 'utf-8').encode()
            msg = MIMEApplication(attachment_data, 'octet-stream', charset='utf-8', name=name)
            msg.add_header('Content-Disposition', 'attachment', filename=name)
            mail.attach(msg)
        return mail.as_string()



def routes():
    return [
        ( r'/',                     Index        ),
        ( r'/about',                About        ),
        ( r'/search',               SearchBook   ),
        ( r'/recent',               RecentBook   ),
        ( r'/hot',                  HotBook      ),
        ( r'/book',                 BookList     ),
        ( r'/book/add',             BookAdd      ),
        ( r'/book/upload',          BookUpload   ),
        ( r'/book/([0-9]+)',        BookDetail   ),
        ( r'/book/([0-9]+)/delete', BookDelete   ),
        ( r'/book/([0-9]+)/edit',   BookEdit     ),
        ( r'/book/([0-9]+)/rating', BookRating   ),
        ( r'/book/([0-9]+)\.(.+)',  BookDownload ),
        ( r'/book/([0-9]+)/push',   BookPush     ),
        ( r'/book/([0-9]+)/read',   BookRead     ),
        ( r'/book/([0-9]+)/refer',  BookRefer    ),
        ( r'/book/([0-9]+)/refer/set/([0-9]{13})$',  BookReferSet),
        ]
