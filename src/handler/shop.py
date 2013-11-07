#!/usr/bin/env python
#coding=utf8

import datetime
import urllib
import simplejson
import logging
from tornado.web import HTTPError
from handler import BaseHandler
from lib.route import route
from lib.util import sendmsg
from model import Category, CategoryAttr, Shop, ShopAttr, ShopPic, Order, OrderItem, Distribution, User, CreditLog

@route(r'/recomm/', name='recomm') #产品推荐
class RecommHandler(BaseHandler):
    
    def get(self):
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        sq = Shop.select(Shop.name, Shop.ename, Shop.cover, Shop.price).where(Shop.status == 1)
        total = sq.count()
        shops = sq.paginate(page, pagesize)
        
        self.render("shop/recomm.html", shops = shops, total = total, page = page, pagesize = pagesize)
    
@route(r'/list/([^/]+)?', name='list') #蛋糕名录
class ListHandler(BaseHandler):
    
    def get(self, slug):
        ccategory= None
        if slug:
            try:
                ccategory = Category.get(slug = slug)
            except:
                self.redirect("/list/")
                return
        
        keyword = self.get_argument("keyword", None)
        
        page = int(self.get_argument("page", 1))
        order = self.get_argument("order", None)
        
        pagesize = self.settings['admin_pagesize']
        
        categorys = self.get_categorys()
        
        sq = Shop.select(Shop.name, Shop.ename, Shop.cover, Shop.price)
        total = sq.count()
        
        if ccategory:
            sq = sq.where((Shop.cid == ccategory.id) & (Shop.status != 9))
        elif keyword:
            keyword = "%" + keyword + "%"
            sq = sq.where((Shop.name % keyword) & (Shop.status != 9))
        else:
            sq = sq.where((Shop.cid != 2) & (Shop.status != 9))
        
        if order:
            sq = sq.order_by(Shop.orders.desc())
        else:
            sq = sq.order_by(Shop.views.desc())
        
        shops = []
        for shop in sq.paginate(page, pagesize):
            shop.price = shop.price.split("~")[0]
            shops.append(shop)
        
        self.render("shop/list.html", ccategory = ccategory, categorys = categorys, shops = shops, total = total, page = page, pagesize = pagesize)

@route(r'/shop/([^/]+)?', name='shop') #蛋糕详细页
class ShopHandler(BaseHandler):
    
    def get(self, ename):
        
        try:
            shop = Shop.get(ename = ename)
            shop.views = shop.views + 1
            shop.save()
            category = Category.get(id = shop.cid)
        except:
            raise HTTPError(404)
            return
        
        categoryattrs = CategoryAttr.select().where(CategoryAttr.cid == shop.cid)
        shopattrs = ShopAttr.select().where(ShopAttr.sid == shop.id)
        if shop.args:
            shop.args = simplejson.loads(shop.args)
        pics = ShopPic.select().where(ShopPic.sid == shop.id)
        
        recomshops = Shop.select().where((Shop.status == 1) & (Shop.id != shop.id)).paginate(1, 5)
        self.render("shop/shop.html", shop = shop, category = category, categoryattrs = categoryattrs, shopattrs = shopattrs, pics = pics, recomshops = recomshops)

@route(r'/order', name='order') #购物车
class OrderHandler(BaseHandler):
    
    def prepare(self):
        if not self.current_user:
            url = self.get_login_url()
            if "?" not in url:
                url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
            self.redirect(url)
        
        super(BaseHandler, self).prepare()
    
    def get(self):
        orderitems = []
        user = self.current_user
        
        try:
            order = Order.get(uid = user.id, status = 0)
            
            for orderitem in OrderItem.select().where(OrderItem.oid == order.id).dicts():
                try:
                    orderitem['shop'] = Shop.get(id = orderitem['sid'])
                    if orderitem['said'] > 0:
                        orderitem['shopattr'] = ShopAttr.get(id = orderitem['said'])
                    orderitems.append(orderitem)
                except:
                    pass
        except:
            order = Order()
        
        ashops = Shop.select().where((Shop.cid == 2) & (Shop.status != 9))
        self.render("shop/order.html", orderitems = orderitems, order = order, ashops = ashops)

@route(r'/settle', name='settle') #结算
class SettleHandler(BaseHandler):
    
    def prepare(self):
        if not self.current_user:
            url = self.get_login_url()
            if "?" not in url:
                url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
            self.redirect(url)
        
        super(BaseHandler, self).prepare()
    
    def get(self):
        orderitems = []
        user = self.current_user
        
        order = None
        
        distributions = self.get_distributions()
        price = 0.0
        credit = 0.0
        
        try:
            order = Order.get(uid = user.id, status = 0)
            
            try:
                mobile = '18014349809'
                sendmsg(self.settings, mobile, '新订单')
            except:
                pass
                
            for orderitem in OrderItem.select().where(OrderItem.oid == order.id).dicts():
                try:
                    orderitem['shop'] = Shop.get(id = orderitem['sid'])
                    _oiprice = orderitem['shop'].price
                    
                    if orderitem['said'] > 0:
                        orderitem['shopattr'] = ShopAttr.get(id = orderitem['said'])
                        if orderitem['shop'].cid == 1:
                            _oicredit = orderitem['shopattr'].price
                            credit = credit + _oicredit * orderitem['num']
                        else:
                            _oiprice = orderitem['shopattr'].price
                    else:
                        _oiprice = float(_oiprice)
                    
                    orderitems.append(orderitem)
                    
                    price = price + _oiprice * orderitem['num']
                    
                except:
                    pass
            order.price = price
            order.save()
            
        except:
            pass
        
        if orderitems:
            self.render("shop/settle.html", tmday = datetime.date.today() + datetime.timedelta(days=1), order  = order, orderitems = orderitems, distributions = distributions.values(), credit = credit)
    
    def post(self):
        order = None
        user = self.get_current_user()
        
        try:
            order = Order.get(uid = user.id, status = 0)
            
            mobile = self.get_argument("mobile", user.mobile)
            uaid = self.get_argument("uaid", None)
            distrid = self.get_argument("distrid", None)
            day = self.get_argument("day", datetime.date.today() + datetime.timedelta(days=1))
            hour = int(self.get_argument("hour", 10))
            payment = self.get_argument("payment", 0)
            message = self.get_argument("message", "")
            isinvoice = self.get_argument("isinvoice", 0)
            invoicesub = self.get_argument("invoicesub", 0)
            invoicename = self.get_argument("invoicename", "")
            invoicecontent = self.get_argument("payment", 1)
            shippingprice = self.get_argument("shippingprice", 0.0)
            
            if uaid and distrid:
                try:
                    distrib = Distribution.get(id = distrid)
                    shippingprice = distrib.price
                except:
                    pass
                
                order.mobile = mobile
                order.uaid = uaid
                order.distrid = distrid
                order.distribbed = "%s %d:00:00" % (str(day), hour)
                order.payment = payment
                order.message = message
                
                order.isinvoice = isinvoice
                
                if isinvoice:
                    order.invoicesub = invoicesub
                    order.invoicename = invoicename
                    order.invoicecontent = invoicecontent
                
                order.shippingprice = shippingprice
                
                order.save()
                
                
                    
                body = ""
                for orderitem in OrderItem.select().where(OrderItem.oid == order.id).dicts():
                        
                    try:
                        shop = Shop.get(id = orderitem['sid'])
                            
                        sname = ""
                        if orderitem['said'] > 0:
                            shopattr = ShopAttr.get(id = orderitem['said'])
                            
                            if shop.cid == 1:
                                credits = shopattr.price * orderitem['num']
                                
                                if credits > user.credit:
                                    OrderItem.delete().where(OrderItem.id == orderitem['id']).execute()
                                else:
                                    user = User.get(id = user.id)
                                    user.credit = user.credit - credits
                                    user.save()
                                    
                                    clog = CreditLog()
                                    clog.uid = user.id
                                    clog.mobile = user.mobile
                                    clog.ctype = 1
                                    clog.affect = int(credits)
                                    clog.log = u"购买" + shop.name
                                    clog.save()
                                    
                                    self.session['user'] = user
                                    self.session.save()
                                    
                            sname = shopattr.name
                            
                        body = body + shop.name + " " + sname + " " + str(orderitem['num']) + "个\n"
                    except Exception, ex:
                        logging.error(ex)
                
                tn = "U%d-S%d" % (user.id, order.id)
                
                if int(payment) == 1:
                    self.redirect("/alipay/topay?tn=%s&body=%s&price=%f" % (tn, body, order.price))
                else:
                    self.flash(u"请选择地址和收货方式")
                    self.redirect("/user/orders")
            else:
                self.flash(u"请选择地址和收货方式")
                self.redirect(self.request.headers["Referer"])
        except Exception, ex:
            logging.error(ex)
            self.flash(u"此订单不存在或者已过期")