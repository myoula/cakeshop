#!/usr/bin/env python
#coding=utf8

import re
import urllib
import simplejson

def setting_from_object(obj):
    setting = dict()
    for key in dir(obj):
        if key.isupper():
            setting[key.lower()] = getattr(obj, key)
    return setting

def find_subclasses(klass, include_self=False):
    accum = []
    for child in klass.__subclasses__():
        accum.extend(find_subclasses(child, True))
    if include_self:
        accum.append(klass)
    return accum

def vmobile(mobile):
    return re.match(r"((13|14|15|18)\d{9}$)|(\w+[@]\w+[.]\w+)", mobile)

def sendmsg(settings, mobile, content):
    url = "%s?accesskey=%s&secretkey=%s&mobile=%s&content=%s" % (settings['sms_gateway'], settings['sms_key'], settings['sms_secret'], mobile, urllib.quote_plus(content))
    result = simplejson.loads(urllib.urlopen(url).read())
    
    if int(result['result']) > 1:
        raise Exception('无法发送')