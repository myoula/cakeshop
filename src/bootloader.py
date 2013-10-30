#!/usr/bin/env python
#coding=utf8

import os
from jinja2 import Environment, FileSystemLoader
from jinja2 import MemcachedBytecodeCache
import setting
from lib.util import setting_from_object
from lib.database import Db
from lib import uimodules
import memcache

settings = setting_from_object(setting)

settings.update({
        'template_path':os.path.join(os.path.dirname(__file__), 'template'),
        'static_path':os.path.join(os.path.dirname(__file__), 'style'),
        'upload_path':os.path.join(os.path.dirname(__file__), 'upload'),
        'cookie_secret':"SZUzonpBQIuXE3yKBtWPre2N5AS7jEQKv0Kioj9iKT0=",
        'login_url':'/signin',
        "xsrf_cookies": True,
        'ui_modules' : uimodules,
        'autoescape':None
    })

memcachedb = memcache.Client([settings['memcache_host']])

bcc = None
if settings['debug'] == False:
    bcc = MemcachedBytecodeCache(memcachedb)

jinja_environment = Environment(
            loader = FileSystemLoader(settings['template_path']),
            bytecode_cache = bcc,
            auto_reload = settings['debug'],
            autoescape = False)

db = Db({'db':settings['db_name'], 'host':settings['db_host'], 'port':settings['db_port'], \
               'user':settings['db_user'], 'passwd':settings['db_passwd'], 'charset':'utf8'})