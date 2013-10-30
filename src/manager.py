#!/usr/bin/env python
#coding=utf8

import time
import signal
import logging
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import define, parse_command_line, options

from bootloader import settings, jinja_environment, memcachedb
from lib.filter import register_filters
from lib.route import Route
from lib.session import MemcacheSessionStore
from handler import site, admin, ajax, oauth, shop, pay, user

define('cmd', default='runserver', metavar='runserver|syncdb')
define('port', default=8080, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        self.jinja_env = jinja_environment
        self.jinja_env.filters.update(register_filters())
        self.jinja_env.tests.update({})
        self.jinja_env.globals['settings'] = settings
        
        self.memcachedb = memcachedb
        self.session_store = MemcacheSessionStore(memcachedb)
        
        handlers = [
                    tornado.web.url(r"/style/(.+)", tornado.web.StaticFileHandler, dict(path=settings['static_path']), name='static_path'),
                    tornado.web.url(r"/upload/(.+)", tornado.web.StaticFileHandler, dict(path=settings['upload_path']), name='upload_path')
                    ] + Route.routes()
        tornado.web.Application.__init__(self, handlers, **settings)

def syncdb():
    from lib.util import find_subclasses
    from model import db, User, Distribution, Category, Page
    
    models = find_subclasses(db.Model)
    for model in models:
        if model.table_exists():
            model.drop_table()
        model.create_table()
        logging.info('created table:%s' % model._meta.db_table)
    
    User.create(mobile = 'root', password = User.create_password('111111'), group = 9)
    Distribution.create(name = '免费配送', price = 0)
    Distribution.create(name = '上门自提', price = 0)
    Category.create(name = '积分商品', slug = 'credit', order = 1)
    Category.create(name = '搭配购买', slug = 'acc', order = 2)
    Category.create(name = '慕斯蛋糕', slug = 'mousse', order = 3)
    Category.create(name = '巧克力蛋糕', slug = 'chocolate', order = 4)
    Category.create(name = '乳酪蛋糕', slug = 'cheese', order = 5)
    Category.create(name = '乳脂奶油蛋糕', slug = 'creambutter', order = 6)
    Category.create(name = '冰淇淋蛋糕', slug = 'icecream', order = 7)
    Page.create(name = '吉米的厨房', slug = 'aboutus', content = '')
    Page.create(name = '包装展示', slug = 'bzzs', content = '')
    Page.create(name = '订购说明', slug = 'dgsm', content = '')
    Page.create(name = '如何收货', slug = 'rhsh', content = '')
    Page.create(name = '付款方式', slug = 'fkfs', content = '')
    Page.create(name = '配送范围', slug = 'psfw', content = '')
    
    logging.info('superuser - username:root password:111111')

def runserver():
    http_server = HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    
    loop = tornado.ioloop.IOLoop.instance()
    
    def shutdown():
        logging.info('Server stopping ...')
        http_server.stop()
        
        logging.info('IOLoop wil  be terminate in 1 seconds')   
        deadline = time.time() + 1
        
        def terminate():
            now = time.time()
            
            if now < deadline and (loop._callbacks or loop._timeouts):
                loop.add_timeout(now + 1, terminate)
            else:
                loop.stop()
                logging.info('Server shutdown')
        
        terminate()
    
    def sig_handler(sig, frame):
        logging.warn('Caught signal:%s', sig)
        loop.add_callback(shutdown)
    
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    
    logging.info('Server running on http://0.0.0.0:%d'%(options.port))
    loop.start()

if __name__ == '__main__':
    parse_command_line()
    
    if options.cmd == 'syncdb':
        syncdb()
    else:
        runserver()
    
