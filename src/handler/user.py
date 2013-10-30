#!/usr/bin/env python
#coding=utf8

import datetime
import logging
from handler import UserBaseHandler
from lib.route import route
from lib.util import vmobile
from model import User, Order, OrderItem, Shop, ShopAttr, UserAddr, Consult, Mark, CreditLog

@route(r'/user', name='user') #用户后台首页
class UserHandler(UserBaseHandler):
    
    def get(self):
        user = self.get_current_user()
        try:
            user = User.get(id = user.id)
            self.session['user'] = user
            self.session.save()
        except:
            pass
        
        self.render('user/index.html')

@route(r'/user/profile', name='user_profile') #用户资料
class ProfileHandler(UserBaseHandler):
    
    def get(self):
        self.render('user/profile.html')
    
    def post(self):
        realname = self.get_argument('realname', '')
        gender = int(self.get_argument('gender', 2))
        birthday = self.get_argument('birthday', '')
        qq = self.get_argument('qq', '')
        tel = self.get_argument('tel', '')
        
        user = self.get_current_user()
        
        try:
            user = User.get(id = user.id)
            user.realname = realname
            user.gender = gender
            user.birthday = birthday
            user.qq = qq
            user.tel = tel
            user.save()
            self.session['user'] = user
            self.session.save()
            self.flash("修改成功", "success")
        except:
            self.flash("修改资料失败")
        
        self.redirect('/user/profile')

@route(r'/user/orders', name='user_orders') #用户订单
class OrderHandler(UserBaseHandler):
    
    def get(self):
        user = self.get_current_user()
        status = self.get_argument("status", None)
        
        ft = (Order.uid == user.id)
        
        if status:
            ft = ft & (Order.status == status)
        
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        oq = Order.select().where(ft)
        total = oq.count()
        
        orders = []
        for order in oq.paginate(page, pagesize).dicts():
            order['orderitems'] = []
            
            for orderitem in OrderItem.select().where(OrderItem.oid == order['id']).dicts():
                
                try:
                    orderitem['shop'] = Shop.get(id = orderitem['sid'])
                    if orderitem['said'] > 0:
                        orderitem['shopattr'] = ShopAttr.get(id = orderitem['said'])
                except:
                    break
                
                order['orderitems'].append(orderitem)
            
            if order['orderitems']:
                orders.append(order)
                
            else:
                Order.delete().where(Order.id == order['id']).execute()
                
                try:
                    user = User.get(id = user.id)
                    
                    if user.order > 0:
                        user.order = user.order - 1
                        user.save()
                        self.session['user'] = user
                        self.session.save()
                except:
                    pass
                
        
        self.render('user/order.html', orders = orders, total = total, page = page, pagesize = pagesize)

@route(r'/user/address', name='user_address') #用户地址
class AddressHandler(UserBaseHandler):
    
    def get(self):
        user = self.get_current_user()
        address = [addr for addr in UserAddr.select().where(UserAddr.uid == user.id)]
        self.render('user/address.html', address = address, useraddr = UserAddr(mobile = user.mobile))
    
    def post(self):
        
        city = self.get_argument("city", None)
        region = self.get_argument("region", None)
        address = self.get_argument("address", None)
        name = self.get_argument("name", None)
        tel = self.get_argument("tel", "")
        mobile = self.get_argument("mobile", None)
        
        if city and region and address and name and mobile and vmobile(mobile):
            user = self.get_current_user()
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
                self.flash("此地址已存在")
            except:
                try:
                    useraddr.save()
                    self.flash("保存成功", 'sucess')
                except Exception, ex:
                    logging.error(ex)
                    self.flash("系统出错，请稍后重试")
        else:
            self.flash("请输入必填项")
        
        self.redirect("/user/address")

@route(r'/user/editaddress/(\d+)', name='user_editaddress')
class EditAddress(UserBaseHandler):
    
    def get(self, aid):
        try:
            useraddr = UserAddr.get(id = aid)
        except:
            self.flash("此地址不存在")
            self.redirect("/user/address")
            return
        
        user = self.get_current_user()
        address = [addr for addr in UserAddr.select().where(UserAddr.uid == user.id)]
        self.render('user/address.html', address = address, useraddr = useraddr)
    
    def post(self, aid):
        
        try:
            useraddr = UserAddr.get(id = aid)
        except:
            self.flash("此地址不存在")
            self.redirect("/user/address")
            return
        
        user = self.get_current_user()
        city = self.get_argument("city", None)
        region = self.get_argument("region", None)
        address = self.get_argument("address", None)
        name = self.get_argument("name", None)
        tel = self.get_argument("tel", "")
        mobile = self.get_argument("mobile", None)
        
        if city and region and address and name and mobile and vmobile(mobile):
            useraddr.city = city
            useraddr.region = region
            useraddr.address = address
            useraddr.name = name
            useraddr.tel = tel
            useraddr.mobile = mobile
                
            try:
                UserAddr.get(id != useraddr.id, uid = user.uid, address = address)
                self.flash("此地址已存在")
            except:
                try:
                    useraddr.save()
                    self.flash("保存成功", 'sucess')
                except Exception, ex:
                    logging.error(ex)
                    self.flash("系统出错，请稍后重试")
        else:
            self.flash("请输入必填项")
        
        self.redirect("/user/address")

@route(r'/user/deladdress/(\d+)', name='user_deladdress')
class DelAddress(UserBaseHandler):
    
    def get(self, aid):
        user = self.get_current_user()
        UserAddr.delete().where(UserAddr.uid == user.id, UserAddr.id == aid).execute()
        self.flash("删除成功")
        self.redirect("/user/address")

@route(r'/user/password', name='user_password') #修改密码
class PasswordHandler(UserBaseHandler):
    
    def get(self):
        self.render('user/password.html')
    
    def post(self):
        opassword = self.get_argument("opassword", None)
        password = self.get_argument("password", None)
        apassword = self.get_argument("apassword", None)
        
        if opassword and password and apassword:
            if len(password) < 6:
                self.flash("请确认输入6位以上新密码")
            elif password != apassword:
                    self.flash("请确认新密码和重复密码一致")
            else:
                user = self.get_current_user()
                if user.check_password(opassword):
                    user.password = User.create_password(password)
                    user.save()
                    
                    self.flash("修改密码成功，请重新登陆。", 'ok')
                    self.redirect("/signout?next=/signin")
                    return
                else:
                    self.flash("请输入正确的老密码")
        else:
            self.flash("请输入老密码和新密码")
        
        self.render('user/password.html')

@route(r'/user/consults', name='user_consults') #用户咨询
class ConsultHandler(UserBaseHandler):
    
    def get(self):
        user = self.get_current_user()
        
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        cq = Consult.select().where(Consult.uid == user.id)
        total = cq.count()
        consults = []
        for consult in cq.paginate(page, pagesize).order_by(Consult.replyed.desc(), Consult.posted.desc()).dicts():
            try:
                shop = Shop.get(id = consult['sid'])
            except:
                shop = Shop
            consult['shop'] = shop
            consults.append(consult)
        
        self.render('user/consult.html', consults = consults, total = total, page = page, pagesize = pagesize)

@route(r'/user/credits', name='user_credits') #用户积分
class CreditHandler(UserBaseHandler):
    
    def get(self):
        user = self.get_current_user()
        
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        cq = CreditLog.select().where(CreditLog.uid == user.id)
        total = cq.count()
        clogs = cq.paginate(page, pagesize)
        
        self.render('user/credit.html', clogs = clogs, total = total, page = page, pagesize = pagesize)


@route(r'/user/marks', name='user_marks') #用户纪念日
class MarkHandler(UserBaseHandler):
    
    def get(self):
        user = self.get_current_user()
        
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        mq = Mark.select().where(Mark.uid == user.id)
        total = mq.count()
        marks = mq.paginate(page, pagesize)
        
        self.render('user/mark.html', marks = marks, total = total, page = page, pagesize = pagesize, mark = Mark(day = datetime.date.today() + datetime.timedelta(days=1)))
    
    def post(self):
        nickname = self.get_argument("nickname", None)
        name = self.get_argument("name", None)
        relation = int(self.get_argument("relation", 0))
        gender = int(self.get_argument("gender", 0))
        day = self.get_argument("day", datetime.date.today() + datetime.timedelta(days=1))
        mobile = self.get_argument("mobile", None)
        
        if nickname and name and mobile and vmobile(mobile):
            user = self.get_current_user()
            mark = Mark()
            mark.uid = user.id
            mark.nickname = nickname
            mark.name = name
            mark.relation = relation
            mark.gender = gender
            mark.day = day
            mark.mobile = mobile
            
            try:
                Mark.get(uid = user.uid, nickname = nickname)
                self.flash("此纪念日已存在")
            except:
                try:
                    mark.save()
                    self.flash("保存成功", 'sucess')
                except Exception, ex:
                    logging.error(ex)
                    self.flash("系统出错，请稍后重试")
        else:
            self.flash("请输入必填项")
        
        self.redirect("/user/marks")

@route(r'/user/editmark/(\d+)', name='user_editmark')
class EditMark(UserBaseHandler):
    
    def get(self, mid):
        try:
            mark = Mark.get(id = mid)
        except:
            self.flash("此地址不存在")
            self.redirect("/user/marks")
            return
        
        user = self.get_current_user()
        
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        mq = Mark.select().where(Mark.uid == user.id)
        total = mq.count()
        marks = mq.paginate(page, pagesize)
        
        self.render('user/mark.html', marks = marks, total = total, page = page, pagesize = pagesize, mark = mark)

    
    def post(self, mid):
        
        try:
            mark = Mark.get(id = mid)
        except:
            self.flash("此地址不存在")
            self.redirect("/user/marks")
            return
        
        nickname = self.get_argument("nickname", None)
        name = self.get_argument("name", None)
        relation = int(self.get_argument("relation", 0))
        gender = int(self.get_argument("gender", 0))
        day = self.get_argument("day", datetime.date.today() + datetime.timedelta(days=1))
        mobile = self.get_argument("mobile", None)
        
        if nickname and name and mobile and vmobile(mobile):
            user = self.get_current_user()
            mark.nickname = nickname
            mark.name = name
            mark.relation = relation
            mark.gender = gender
            mark.day = day
            mark.mobile = mobile
                
            try:
                Mark.get(id != mark.id, uid = user.uid, nickname = nickname)
                self.flash("此纪念日已存在")
            except:
                try:
                    mark.save()
                    self.flash("保存成功", 'sucess')
                except Exception, ex:
                    logging.error(ex)
                    self.flash("系统出错，请稍后重试")
        else:
            self.flash("请输入必填项")
        
        self.redirect("/user/marks")

@route(r'/user/delmark/(\d+)', name='user_delmark')
class DelMark(UserBaseHandler):
    
    def get(self, mid):
        user = self.get_current_user()
        Mark.delete().where(Mark.uid == user.id, Mark.id == mid).execute()
        self.flash("删除成功")
        self.redirect("/user/marks")