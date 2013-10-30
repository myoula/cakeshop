#!/usr/bin/env python
#coding=utf8

import os
import time
import random
import simplejson
from PIL import Image, ImageFont, ImageDraw
import StringIO
import logging

from handler import BaseHandler
from lib.route import route
from lib.util import vmobile, sendmsg
from model import UserAddr, UserVcode, Shop, ShopAttr, Order, OrderItem, Consult, Area

@route(r'/ajax/upload', name='ajax_upload') #上传文件
class UploadHandler(BaseHandler):
    
    def check_xsrf_cookie(self):
        pass
    
    def post(self):
        if self.request.files:
            ext = self.request.files["filedata"][0]["filename"].rsplit('.')[-1].lower()
            
            msg = 'forbbiden file'
            
            if ext in ['jpg', 'gif', 'png']:
                filename = '%d%d.%s' %(int(time.time()), random.randint(1000, 9999), ext)
                
                try:
                    with open('upload/' + filename, "wb") as f:
                        f.write(self.request.files["filedata"][0]["body"])
                        msg = '/upload/' + filename
                except:
                    msg = '上传失败'
            
            self.write('{"err":"","msg":"%s"}' % msg)

@route(r'/ajax/vcode', name='ajax_vcode') #手机验证码
class VcodeHandler(BaseHandler):
    
    def get(self):
        result = {'status':False, 'msg':''}
        mobile = self.get_argument("mobile", None)
        
        UserVcode.delete().where(UserVcode.created < (int(time.time()) - 2 * 3600)).execute()
        
        uservcode = UserVcode()
        uservcode.mobile = mobile
        uservcode.vcode = random.randint(1000, 9999)
        
        try:
            uservcode.validate()
            
            if UserVcode.select().where(UserVcode.mobile == mobile).count() > 3:
                result['msg'] = 503
            else:
                try:
                    sendmsg(self.settings, mobile, "您在吉米的厨房获取的验证码为" + str(uservcode.vcode))
                    uservcode.save()
                    
                    logging.info("sendmsg:%s - %d" % (mobile, uservcode.vcode))
                    
                    result['status'] = True
                    result['msg'] = uservcode.vcode
                except Exception, ex:
                    logging.error(ex)
                    result['msg'] = 500
            
        except Exception, ex:
            logging.error(ex)
            result['msg'] = 400
 
        self.write(simplejson.dumps(result))

@route(r'/ajax/captcha', name='ajax_captcha')
class CaptchaHandler(BaseHandler):
    
    def get(self):
        img = Image.new('RGB',size=(40,16),color=(255,255,255))
        draw = ImageDraw.Draw(img)
        captcha = str(random.randint(1000, 9999))
        self.set_cookie("captcha", captcha)
        
        font = ImageFont.truetype(os.path.join(os.path.dirname(__file__).replace('handler', 'upload'),'Arial.ttf'), 12)
        for i,s in enumerate(captcha):
            position = (i*10, 2)
            draw.text(position, s, fill=(0,0,0), font = font)
        
        del draw
        strIO = StringIO.StringIO()
        img.save(strIO, 'png')
        strIO.seek(0)
        self.set_header("Content-Type", "image/png")
        self.write(strIO.read())

@route(r'/ajax/addshop', name='ajax_addshop')
class AddShopHandler(BaseHandler):
    
    def post(self):
        
        result = {'status' : False, 'msg' : 0}
        user = self.get_current_user()
        
        if user:
            sid = int(self.get_argument("sid", 0))
            said = int(self.get_argument("said", 0))
            num = int(self.get_argument("num", 1))
            
            #判断商品是否下架
            if sid > 0 and said > 0 and num > 0:
                try:
                    Shop.get(id = sid)
                    ShopAttr.get(id = said)
                    
                    #判断是否有未使用的订单或生成新订单
                    try:
                        try:
                            order = Order.get(uid = user.id, status = 0)
                        except:
                            order = Order()
                            order.uid = user.id
                            order.mobile = user.mobile
                            order.ordered = int(time.time())
                            try:
                                order.save()
                            except Exception, ex:
                                logging.error(ex)
                        
                        try:
                            orderitem = OrderItem.get(oid = order.id, sid = sid, said = said)
                        except:
                            orderitem = OrderItem()

                        orderitem.oid = order.id
                        orderitem.sid = sid
                        orderitem.said = said
                        orderitem.num = orderitem.num + num
                        orderitem.save()
                        
                        result['status'] = True
                        result['msg'] = 200
                        
                    except Exception, ex:
                        logging.error(ex)
                        result['msg'] = 500
                    
                except:
                    result['msg'] = 404
            else:
                result['msg'] = 400
        else:
            result['msg'] = 403
            
        self.write(simplejson.dumps(result))

@route(r'/ajax/comment/([0-9]+)', name='ajax_comment')
class CommentHandler(BaseHandler):
    
    def post(self, sid):
        result = {'status' : False, 'msg' : 0}
        captcha = self.get_cookie("captcha")
        user = self.get_current_user()
        
        if captcha and user:
            content = self.get_argument("content", None)
            vcode = self.get_argument("vcode", None)
            
            if content and vcode and len(vcode) == 4:
                if vcode == captcha:
                    consult = Consult()
                    consult.uid = user.id
                    consult.sid = sid
                    consult.mobile = user.mobile
                    consult.content = content
                    try:
                        consult.save()
                        result['status'] = True
                        result['msg'] = 200
                    
                    except Exception, ex:
                        logging.error(ex)
                        result['msg'] = 500
                else:
                    result['msg'] = 401
            else:
                result['msg'] = 400
        else:
            result['msg'] = 403
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/consults/([0-9]+)', name='ajax_consults')
class ConsultsHandler(BaseHandler):
    
    def get(self, sid):
        
        result = {'total' : 0, 'pages' : 0, 'data' : []}
        page = self.get_argument("page", 1)
        total = Consult.select().where(Consult.sid == sid).count()
        
        pages = 0
        if total > 0:
            pages = total / 20
        page = int(page)

        if total % 20 > 0:
            pages = pages + 1
        
        result['total'] = total
        result['pages'] = pages
        
        if total > 0:
            result['data'] = [consult for consult in Consult.select().where(Consult.sid == sid).order_by(Consult.replyed.desc()).paginate(page).dicts()]
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/changeorder', name='ajax_changeorder')
class ChangeOrderHandler(BaseHandler):
    
    def post(self):
        result = {'status' : False, 'msg' : 0}
        user = self.get_current_user()
        
        if user:
            oiid = int(self.get_argument("oiid", 0))
            num = int(self.get_argument("num", 1))
            
            if (oiid > 0 and num > 0):
                try:
                    orderitem = OrderItem.get(id = oiid)
                    orderitem.num = num
                    
                    try:
                        orderitem.save()
                        result['status'] = True
                        result['msg'] = 200
                    
                    except Exception, ex:
                        logging.error(ex)
                        result['msg'] = 500
                except:
                    result['msg'] = 404
            else:
                result['msg'] = 400  
        else:
            result['msg'] = 403
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/delorder/(\d+)', name='ajax_delorder')
class DelOrderHandler(BaseHandler):
    
    def get(self, oiid):
        result = {'status' : False, 'msg' : 0}
        user = self.get_current_user()
        
        if user:
            try:
                orderitem  = OrderItem.get(id = oiid)
                order = Order.get(id = orderitem.oid)
                
                if order.uid == user.id:
                    if OrderItem.select().where(OrderItem.oid == orderitem.oid).count() == 1:
                        order.delete_instance()
                        
                        if user.order > 0:
                            user.order = user.order - 1
                            user.save()
                            self.session['user'] = user
                            self.session.save()
                    
                    orderitem.delete_instance()
                    result['status'] = True
                    result['msg'] = 200
                    
                else:
                    result['msg'] = 403
                
            except Exception, ex:
                logging.error(ex)
                result['msg'] = 500
        else:
            result['msg'] = 403
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/orderacc/(\d+)/(\d+)', name='ajax_orderacc')
class OrderAccHandler(BaseHandler):
    
    def post(self, oid, sid):
        
        result = {'status' : False, 'msg' : 0}
        user = self.get_current_user()
        
        if user:
            try:
                order = Order.get(id = oid)
                
                if order.uid == user.id:
                    try:
                        orderitem = OrderItem.get(OrderItem.oid == oid, OrderItem.sid == sid)
                    except:
                        orderitem = OrderItem()
                    
                    orderitem.oid = oid
                    orderitem.sid = sid
                    orderitem.num = orderitem.num + 1
                    
                    try:
                        orderitem.save()
                        result['status'] = True
                        result['msg'] = 200
                    except Exception, ex:
                        logging.error(ex)
                        result['msg'] = 500
                else:
                    result['msg'] = 403
            except:
                result['msg'] = 404
            
        else:
            result['msg'] = 403
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/useraddrs', name='ajax_useraddrs')
class UserAddrsHandler(BaseHandler):
    
    def get(self):
        user = self.get_current_user()
        result = []
        
        if user:
            result = [useraddr for useraddr in UserAddr.select().where(UserAddr.uid == user.id).dicts()]
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/addaddr', name='ajax_addr')
class AddAddrHandler(BaseHandler):
    
    def post(self):
        result = {'status' : False, 'msg' : 0}
        user = self.get_current_user()
        
        if user:
            city = self.get_argument("city", None)
            region = self.get_argument("region", None)
            address = self.get_argument("address", None)
            name = self.get_argument("name", None)
            tel = self.get_argument("tel", "")
            mobile = self.get_argument("mobile", None)
            
            if city and region and address and name and mobile and vmobile(mobile):
                useraddr = UserAddr()
                useraddr.uid = user.id
                useraddr.city = city
                useraddr.region = region
                useraddr.address = address
                useraddr.name = name
                useraddr.tel = tel
                useraddr.mobile = mobile
                
                try:
                    UserAddr.get(uid = user.uid, address = address)
                    result['msg'] = 503
                    
                except:
                    try:
                        useraddr.save()
                        result['status'] = True
                        result['msg'] = 200
                    
                    except Exception, ex:
                        logging.error(ex)
                        result['msg'] = 500
            else:
                result['msg'] = 400
        else:
            result['msg'] = 403
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/deladdr/([0-9]+)', name='ajax_deladdr')
class DelAddrHandler(BaseHandler):
    
    def get(self, uaid):
        
        result = {'status' : False, 'msg' : 0}
        user = self.get_current_user()
        
        if user:
            try:
                UserAddr.delete().where(UserAddr.id == uaid).execute()
                result['status'] = True
                result['msg'] = 200
            except Exception, ex:
                logging.error(ex)
                result['msg'] = 500
        else:
            result['msg'] = 403
        
        self.write(simplejson.dumps(result))

@route(r'/ajax/areas', name='ajax_areas')
class AreaHandler(BaseHandler):
    
    def get(self):
        areas = []
        
        for area in Area.select().where(Area.pid == 0).dicts():
            areas.append(area)
            
            for carea in Area.select().where(Area.pid == area['id']).dicts():
                areas.append(carea)
        
        self.write(simplejson.dumps(areas))