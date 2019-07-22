#!/usr/bin/python
#-*- coding: UTF-8 -*-

import sys
import logging
from urllib import quote_plus as urlencode


def json_output(self, vals):
    b = vals['book']
    host = 'https://'+self.request.host

    def get(k, default=_("Unknown")):
        v = b.get(k, None)
        if not v: v = default
        return v

    collector = b.get('collector', {}).get('username', None)
    try:
        pubdate = b['pubdate'].strftime("%Y-%m-%d"),
    except:
        pubdate = None

    d = {
        'id':              b['id'],
        'title':           b['title'],
        'rating':          b['rating'],
        'count_visit':     b['count_visit'],
        'count_download':  b['count_download'],
        'timestamp':       b['timestamp'].strftime("%Y-%m-%d"),
        'pubdate':         pubdate,
        'collector':       collector,
        'author':          ', '.join(b['authors']),
        'tags':            ' / '.join(b['tags']),
        'author_sort':     get('author_sort'),
        'publisher':       get('publisher'),
        'comments':        get('comments',  _(u'暫無簡介') ),
        'series':          get('series',    None),
        'language':        get('language',  None),
        'isbn':            get('isbn',      None),

        "cover_large_url": host+"/get/thumb_600_840/%(id)s.jpg?t=%(timestamp)s" % b,
        "cover_url":       host+"/get/thumb_155_220/%(id)s.jpg?t=%(timestamp)s" % b,
        }
    return d

