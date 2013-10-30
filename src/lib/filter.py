#!/usr/bin/env python
#coding=utf8

import time

def datetimeformat(value, fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt, time.localtime(value))

def truncate_words(s, num=50, end_text='...'):
    s = unicode(s,'utf8')
    length = int(num)
    if len(s) > length:
        s = s[:length]
        if not s[-1].endswith(end_text):
            s= s+end_text
    return s

def null(value):
    return value if value else ""


def register_filters():
    filters ={}
    filters['truncate_words'] = truncate_words
    filters['datetimeformat'] = datetimeformat
    filters['null'] = null
    return filters