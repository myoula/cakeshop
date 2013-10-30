#!/usr/bin/env python
#coding=utf-8

import re
import time
import datetime
import hashlib
from bootloader import db, memcachedb
from playhouse.signals import connect, post_save
from lib.util import vmobile

#地区表
class Area(db.Model):
    id = db.TinyPrimaryKeyField()
    pid = db.TinyIntegerField(default = 0)
    name = db.CharField(max_length=30)
    
    def validate(self):
        if self.name:            
            ft = (Area.name == self.name)
            if self.id:
                ft = ft & (Area.id != self.id)
                
            if Area.select().where(ft).count() > 0:
                raise Exception('地区名已存在')
    
        else:
            raise Exception('请输入地区名')
    
    class Meta:
        db_table = 'areas'

#首页banner
class Ad(db.Model):
    id = db.TinyPrimaryKeyField()
    url = db.CharField(max_length = 50) #商品连接地址
    
    def validate(self):
        if not self.url:
            raise Exception('情输入访问url')
    
    class Meta:
        db_table = 'ads'
    
#用户
class User(db.Model):
    id = db.PrimaryKeyField()
    mobile = db.CharField(unique = True, max_length = 11, null = False) #注册手机号
    password = db.CharField(max_length = 32) #密码
    realname = db.CharField(max_length = 10) #真实姓名
    gender = db.TinyIntegerField(max_length = 1, default = 2) #性别 0男 1女 2未知
    qq = db.CharField(max_length = 15) #qq
    birthday = db.DateField(default = '1980-01-01') #生日
    tel = db.CharField(max_length = 30) #固定电话
    credit = db.SmallIntegerField(default = 0) #积分
    order = db.SmallIntegerField(default = 0) #订单
    consult = db.SmallIntegerField(default = 0) #咨询
    group = db.TinyIntegerField(max_length = 1, default = 1, **{'dbdefault' : 1}) #用户组 0被禁止的用户 1正常用户 9管理员
    signuped = db.IntegerField(default = int(time.time())) #时间
    lsignined = db.IntegerField(default = int(time.time())) #最后登录时间
    
    @staticmethod
    def create_password(raw):
        return hashlib.new("md5", raw).hexdigest()
    
    def check_password(self, raw):
        return hashlib.new("md5", raw).hexdigest() == self.password
    
    def validate(self):
        if self.mobile and vmobile(self.mobile):                
            if User.select().where(User.mobile == self.mobile).count() > 0:
                raise Exception('此用户名已使用')
        else:
            raise Exception('请输入正确的手机号码')
    
    def updatesignin(self):
        self.lsignined = int(time.time())
        self.save()
    
    class Meta:
        db_table = 'users'

#用户联系地址
class UserAddr(db.Model):
    id = db.PrimaryKeyField()
    uid = db.IntegerField(default = 0, index = True)
    city = db.CharField(max_length = 30) #城市
    region = db.CharField(max_length = 30) #区域
    address = db.CharField(max_length = 100) #详细地址
    name = db.CharField(max_length = 10) #姓名
    tel = db.CharField(max_length = 30) #固定电话
    mobile = db.CharField(max_length = 11) #手机号码
    
    class Meta:
        db_table = 'useraddrs'

#手机验证码
class UserVcode(db.Model):
    mobile = db.CharField(max_length = 11, null = False) #注册手机号
    vcode = db.SmallIntegerField(max_length = 4)
    created = db.IntegerField(index = True, default = int(time.time()))
    
    def validate(self):
        if self.mobile and vmobile(self.mobile):
            pass
        else:
            raise Exception('mobile is not validate')
        
    class Meta:
        db_table = 'uservcodes'
        indexes = ((('mobile', 'vcode'), True),)

#第三方登录
class Oauth(db.Model):
    uid = db.IntegerField() #注册用户Id
    src = db.CharField(max_length = 10, choices = ('weibo', 'alipay'), default = 'weibo') #来源
    openid = db.CharField(max_length = 50) #第三方平台用户Id
    
    class Meta:
        db_table = 'oauths'

#免费品尝
class Apply(db.Model):
    coname = db.CharField(max_length = 80) #公司名称
    city = db.CharField(max_length = 30) #城市
    region = db.CharField(max_length = 30) #区域
    address = db.CharField(max_length = 100) #详细地址
    pnumber = db.SmallIntegerField(default = 1) #公司人数
    name = db.CharField(max_length = 10) #姓名
    tel = db.CharField(max_length = 30) #固定电话
    mobile = db.CharField(max_length = 11) #手机号码
    applyed = db.IntegerField(default = int(time.time())) #申请时间
    
    def validate(self):
        if not self.coname:
            raise Exception('请输入公司名')
        
        if not self.region:
            raise Exception('请选择城市')
        
        if not self.region:
            raise Exception('请选择区域')
        
        if not self.address:
            raise Exception('请输入详细地址')
        
        if not self.name:
            raise Exception('请输入姓名')
        
        if not self.tel:
            raise Exception('请输入固定电话')
        
        if self.mobile and not vmobile(self.mobile):
            raise Exception('请输入正确的手机号码')
    
    class Meta:
        db_table = 'applys'
        order_by = ('-applyed',)

#分类
class Category(db.Model):
    id = db.TinyPrimaryKeyField()
    name = db.CharField(max_length = 20) #分类名
    slug = db.CharField(max_length = 20) #访问url
    order = db.TinyIntegerField(default = 1) #排序
    
    def validate(self):
        if self.name and self.slug:
            self.slug = self.slug.lower()
            if not re.match('^[0-9a-z]+$', self.slug):
                raise Exception('访问目录只能是字母和数字组合')
            
            ft = ((Category.name == self.name) | (Category.slug == self.slug))
            if self.id:
                ft = ft & (Category.id != self.id)
                
            if Category.select().where(ft).count() > 0:
                raise Exception('分类同名或者目录同名')
    
        else:
            raise Exception('请输入分类名或者访问目录')
    
    @classmethod
    def maxorder(cls):
        return Category.select().count() + 1
    
    class Meta:
        db_table = 'categorys'
        order_by = ('order',)

#分类属性
class CategoryAttr(db.Model):
    id = db.SmallPrimaryKeyField()
    cid = db.TinyIntegerField(index = True) #商品分类
    name = db.CharField(max_length = 50) #商品参数
    dec = db.CharField(max_length = 255) #默认值
    order = db.TinyIntegerField(default = 1) #参数排序
    
    def validate(self):
        if self.cid and self.name:
            
            ft = ((CategoryAttr.cid == self.cid) & (CategoryAttr.name == self.name))
            
            if self.id:
                ft = ft & (CategoryAttr.id != self.id)
            
            if CategoryAttr.select().where(ft).count() > 0:
                raise Exception('此分类属性已存在')
        else:
            raise Exception('请输入属性名或设置分类id')
    
    @classmethod
    def maxorder(cls, cid):
        return CategoryAttr.select().where(CategoryAttr.cid == cid).count() + 1
    
    class Meta:
        db_table = 'categoryattrs'
        order_by = ('order',)

#商品
class Shop(db.Model):
    id = db.PrimaryKeyField()
    name = db.CharField(max_length = 80) #商品名称
    ename = db.CharField(max_length = 100) #商品英文名称
    price = db.CharField(max_length = 30) #商品价格
    cid = db.IntegerField() #商品分类
    level = db.TinyIntegerField(max_length = 1, default = 3) #甜度
    resume = db.CharField() #简单介绍
    intro = db.TextField() #详细介绍
    prompt = db.TextField() #提示
    args = db.TextField() #参数内容
    cover = db.CharField(max_length=20) #头图
    views = db.SmallIntegerField(default = 0) #点击率
    orders = db.SmallIntegerField(default = 0) #购买次
    status = db.TinyIntegerField(max_length = 1, default = 0) #是否推荐 0不推荐 1推荐 #9删除
    created = db.IntegerField(default = int(time.time()))  #添加时间
    
    def validate(self):
        if self.name and self.ename and self.cid:
            if not re.match('^[0-9a-z]+$', "".join(self.ename.lower().split())):
                raise Exception('英文名只能是字母和数字组合')
        else:
            raise Exception('请输入商品名，英文名或设置所属分类id')
    
    class Meta:
        db_table = 'shops'
        order_by = ('-created',)

#商品属性
class ShopAttr(db.Model):
    id = db.PrimaryKeyField()
    sid = db.IntegerField() #商品Id
    name = db.CharField(max_length = 50) #商品规格
    price = db.FloatField() #商品价格
    order = db.TinyIntegerField(default = 1) #规格排序
    
    def validate(self):
        if self.sid and self.name:
            
            ft = ((ShopAttr.sid == self.sid) & (ShopAttr.name == self.name))
            
            if self.id:
                ft = ft & (ShopAttr.id != self.id)
            
            if ShopAttr.select().where(ft).count() > 0:
                raise Exception('此规格已存在')
        else:
            raise Exception('请输入规格，价格或设置分类id')
    
    @classmethod
    def maxorder(cls, sid):
        return ShopAttr.select().where(ShopAttr.sid == sid).count() + 1
    
    class Meta:
        db_table = 'shopattrs'
        order_by = ('order',)

#商品附图
class ShopPic(db.Model):
    id = db.PrimaryKeyField()
    sid = db.IntegerField() #商品Id
    path = db.CharField(max_length=20)
    
    class Meta:
        db_table = 'shoppics'

#咨询
class Consult(db.Model):
    sid = db.IntegerField() #商品Id
    uid = db.IntegerField(default = 0) #用户Id
    mobile = db.CharField(max_length = 11) #用户名
    content = db.TextField() #咨询内容
    posted = db.IntegerField(default = int(time.time())) #咨询时间
    reply = db.TextField() #回复内容
    replyed = db.IntegerField(default = 0) #回复时间
    
    class Meta:
        db_table = 'consults'

#配送方式
class Distribution(db.Model):
    id = db.TinyPrimaryKeyField()
    pdid = db.TinyIntegerField() #是否为第一级
    name = db.CharField(max_length = 20) #配送方式名称
    price = db.FloatField(default = 0.0) #配送价格
    content = db.CharField() #如果为第二级则有内容选择
    
    def validate(self):
        if self.name:
                        
            ft = (Distribution.name == self.name)
            if self.id:
                ft = ft & (Distribution.id != self.id)
                
            if Distribution.select().where(ft).count() > 0:
                raise Exception('此配送方式已存在')
        else:
            raise Exception('请输入配送方式')
    
    class Meta:
        db_table = 'distributions'
        order_by = ('pdid',)
    
#订单
class Order(db.Model):
    id = db.PrimaryKeyField()
    uid = db.IntegerField(default = 0) #用户Id
    mobile = db.CharField(max_length = 11) #注册手机号
    uaid = db.IntegerField(default = 0) #收件地址
    distrid = db.TinyIntegerField(default = 0) #配送方式
    distribbed = db.CharField(max_length=24) #配送时间
    payment = db.TinyIntegerField(max_length = 1, default = 1) #付款方式 0货到付款  1支付宝
    message = db.CharField() #付款留言
    isinvoice = db.TinyIntegerField(max_length = 1, default = 0) #是否开发票
    invoicesub = db.TinyIntegerField(max_length = 1, default = 0) #发票抬头 0个人 1公司
    invoicename = db.CharField(max_length = 80) #个人或公司名称
    invoicecontent = db.TinyIntegerField(max_length = 1, default = 1) #发票类型 0蛋糕 1食品
    shippingprice = db.FloatField(default = 0.0) #配送价格
    price = db.FloatField(default = 0.0) #价格
    status = db.TinyIntegerField(max_length = 1, default = 0) #订单状态 0等待付款 1付款成功 2已送货 3交易完成 4已取消
    ordered = db.IntegerField(default = int(time.time())) #下单时间
    
    class Meta:
        db_table = 'orders'
    
#订单内容
class OrderItem(db.Model):
    oid = db.IntegerField() #订单Id
    sid = db.IntegerField() #商品Id
    said = db.IntegerField() #商品规格Id
    num = db.TinyIntegerField(default = 0) #数量
    
    class Meta:
        db_table = 'orderitems'

#静态页面
class Page(db.Model):
    id = db.TinyPrimaryKeyField()
    name = db.CharField(max_length = 20)
    slug = db.CharField(index = True, max_length = 20) #访问路径
    content = db.TextField() #页面内容
    template = db.CharField(max_length = 20, default = 'staticpage.html')
    
    def validate(self):
        if self.name and self.slug:
            self.slug = self.slug.lower()
            if not re.match('^[0-9a-z]+$', self.slug):
                raise Exception('访问目录只能是字母和数字组合')
            
            ft = ((Page.name == self.name) | (Page.slug == self.slug))
            if self.id:
                ft = ft & (Page.id != self.id)
                
            if Page.select().where(ft).count() > 0:
                raise Exception('分类同名或者目录同名')
        else:
            raise Exception('请输入分类名或者访问目录')
    
    class Meta:
        db_table = 'pages'

#纪念日
class Mark(db.Model):
    id = db.PrimaryKeyField()
    uid = db.IntegerField(default = 0) #用户Id
    nickname = db.CharField(max_length = 10) #昵称
    name = db.CharField(max_length = 20) #名称
    relation = db.TinyIntegerField(max_length = 1, default = 0) #关系 0亲人 1朋友 2同事 3客户
    gender = db.TinyIntegerField(max_length = 1, default = 0) #性别 0男 1女 2未知
    day = db.DateField(default = datetime.date.today()) #时间
    mobile = db.CharField(max_length = 11) #联系手机
    created = db.IntegerField(max_length = 10, default = int(time.time())) #添加时间
    
    class Meta:
        db_table = 'marks'
        order_by = ('-id',)

#积分历史表
class CreditLog(db.Model):
    id = db.PrimaryKeyField()
    uid = db.IntegerField(default = 0) #用户Id
    mobile = db.CharField(max_length = 11) #用户名
    ctype = db.TinyIntegerField(max_length = 1) #扣分 0奖励 1扣除
    affect = db.SmallIntegerField(max_length = 6) #积分
    log = db.CharField(max_length = 100) #说明
    created = db.IntegerField(max_length = 10, default = int(time.time())) #时间
    
    class Meta:
        db_table = 'creditlogs'
        order_by = ('-id',)
    
@connect(post_save,sender=Category)
def resetcategorys(model_class, instance,created):
    categorys = [category for category in Category.select()]
    memcachedb.replace('categorys', categorys, 86400)

@connect(post_save,sender=Distribution)
def resetdistributions(model_class, instance,created):
    distributions = {}
    for distribution in Distribution.select().dicts():
        if distribution['pdid'] == 0:
            distribution['list'] = []
            distributions[distribution['id']] = distribution
        else:
            distributions[distribution['pdid']]['list'].append(distribution)
    memcachedb.replace('distributions', distributions, 86400)

@connect(post_save,sender=ShopAttr)
def resetprice(model_class, instance,created):
    prices = [shopattr.price for shopattr in ShopAttr.select(ShopAttr.price).where(ShopAttr.sid == instance.sid)]
    prices.sort()
    
    if len(prices) > 1:
        price = "%s~%s" % (str(prices[0]), str(prices[-1]))
    else:
        price = str(prices[0])
    
    Shop.update(price = price).where(Shop.id == instance.sid).execute()

@connect(post_save,sender=Order)
def setuserorders(model_class, instance, created):
    if created:
        User.update(order = User.order + 1).where(User.id == instance.uid).execute()