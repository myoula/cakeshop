#!/usr/bin/env python
#coding=utf8

import logging
from handler import BaseHandler
from lib.route import route
from lib.alipay import Alipay
from model import User, Order, CreditLog

@route('/alipay/topay', name='pay_topay') #去支付宝支付
class PayHandler(BaseHandler):
    
    def get(self):
        tn = self.get_argument("tn", None)
        subject = self.get_argument("subject", "购买蛋糕")
        body = self.get_argument("body", "购买蛋糕")
        price = self.get_argument("price", None)
        
        if tn and price:
            price = float(price)
            alipay = Alipay(**self.settings)
            self.redirect(alipay.create_payurl(tn, subject, body, price))

@route('/alipay/return', name='pay_return') #支付宝支付完成后跳转
class ReturnHandler(BaseHandler):
    
    def get(self):
        alipay = Alipay(**self.settings)
        
        params = {}
        ks = self.request.arguments.keys()
        
        for k in ks:
            params[k] = self.get_argument(k)
        
        if alipay.notify_verify(params):
            tn = self.get_argument("out_trade_no", None)
            trade_no = self.get_argument("trade_no", None)
            trade_status = self.get_argument("trade_status", None)
            logging.info("return:%s - %s - %s" % (tn, trade_no, trade_status))
            oid = int(tn.split('-')[1].replace('S', ''))
            
            try:
                order = Order.get(id = oid)
                order.status = 1
                order.save()
                
                user = User.get(id = order.uid)
                user.credit = user.credit + int(order.price)
                user.save()
                
                log = CreditLog()
                log.uid = order.uid
                log.mobile = user.mobile
                log.ctype = 0
                log.affect = int(order.price)
                log.log = u'成功下单 - %s' %  tn
                log.save()
                
                self.session['user'] = user
                self.session.save()
            
                alipay.send_goods_confirm_by_platform(trade_no)
                self.flash("支付成功")
            except Exception, ex:
                logging.error(ex)
            else:
                self.flash("支付失败")
        self.redirect("/pay")

@route(r'/alipay/notify', name='pay_notify') #支付宝异步通知
class NotfiyHandler(BaseHandler):
    
    def check_xsrf_cookie(self):
        pass
    
    def post(self):
        alipay = Alipay(**self.settings)
        
        params = {}
        ks = self.request.arguments.keys()
        
        for k in ks:
            params[k] = self.get_argument(k)
            
        if alipay.notify_verify(params):
            tn = self.get_argument("out_trade_no", None)
            trade_no = self.get_argument("trade_no", None)
            trade_status = self.get_argument("trade_status", None)
            logging.info("notify:%s - %s - %s" % (tn, trade_no, trade_status))
            
            oid = int(tn.split('-')[1].replace('S', ''))
            
            try:
                order = Order.get(id = oid)
                
                if order.status == 0:
                    order.status = 1
                    order.save()
                    
                    user = User.get(id = order.uid)
                    user.credit = user.credit + int(order.price)
                    user.save()
                    
                    log = CreditLog()
                    log.uid = order.uid
                    log.mobile = user.mobile
                    log.ctype = 0
                    log.affect = int(order.price)
                    log.log = u'成功下单 - %s' %  tn
                    log.save()
                
            except Exception, ex:
                logging.error(ex)
            
            if trade_status == 'WAIT_SELLER_SEND_GOODS':
                alipay.send_goods_confirm_by_platform(trade_no)
            
            self.write("success")
        else:
            self.write("fail")