#!/usr/bin/env python
#coding=utf8

DEBUG = True
GZIP = True

DB_HOST= 'localhost'
DB_PORT= 3306
DB_USER = 'root'
DB_PASSWD = 'password'
DB_NAME = 'database'

MEMCACHE_HOST = 'localhost:11211'

ADMIN_PAGESIZE = 20

WEIBO_KEY = ''
WEIBO_SECRET = ''
WEIBO_REDIRECT = 'http://www.xxx.com/oauth/weibo'

ALIPAY_KEY = ''
ALIPAY_INPUT_CHARSET = 'utf-8'
ALIPAY_PARTNER = ''
ALIPAY_SELLER_EMAIL = ''
ALIPAY_SIGN_TYPE = 'MD5'
ALIPAY_AUTH_URL='http://www.xxx.com/oauth/alipay_return'
ALIPAY_RETURN_URL='http://www.xxx.com/alipay/return'
ALIPAY_NOTIFY_URL='http://www.xxx.com/alipay/notify'
ALIPAY_SHOW_URL=''
ALIPAY_TRANSPORT='https'

SMS_KEY = 0
SMS_SECRET = ''
SMS_GATEWAY = 'http://sms.bechtech.cn/Api/send/data/json'
