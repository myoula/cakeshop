#!/usr/bin/env python
#coding=utf8

import time
import simplejson
from handler import AdminBaseHandler
from lib.route import route
from model import User, Category, CategoryAttr, Shop, ShopPic, ShopAttr, Page, Apply, Distribution, Order, OrderItem, Ad, Consult, Area, UserAddr

@route(r'/admin', name='admin_index') #首页
class IndexHandler(AdminBaseHandler):
    
    def get(self):
        self.render('admin/index.html')

@route(r'/admin/users', name='admin_users') #会员管理
class UserHandler(AdminBaseHandler):
    
    def get(self):
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        keyword = self.get_argument("keyword", None)
        
        ft = (User.id > 0)
        
        if keyword:
            keyword = keyword + '%'
            ft = ft & (User.mobile % keyword)
        
        uq = User.select().where(ft)
        total = uq.count()
        users = uq.paginate(page, pagesize).order_by(User.signuped.desc())
        
        self.render('admin/user.html', users = users, total = total, page = page, pagesize = pagesize)

@route(r'/admin/changeuser/(\d+)/(\d+)', name='admin_changeuser') #修改分类
class ChangeUserHandler(AdminBaseHandler):
    
    def get(self, uid, status):
        try:
            user = User.get(id = uid)
            user.group = status
            user.save()
        except:
            pass
        
        self.redirect("/admin/users")

@route(r'/admin/ads', name='admin_ads') #首页广告
class AdHandler(AdminBaseHandler):
    
    def get(self):
        ads = [ad for ad in Ad.select()]
        self.render('admin/ad.html', ads = ads)

@route(r'/admin/addad', name='admin_addad') #添加广告
class AddAdHandler(AdminBaseHandler):
    
    def get(self):
        self.render('admin/addad.html')
    
    def post(self):
        url = self.get_argument("url", None)
        
        if self.request.files:
            ad = Ad()
            ad.url = url
        
            try:
                ad.validate()
                ad.save()
                
                filename = str(ad.id) + ".jpg"
                with open('upload/ad/' + filename, "wb") as f:
                    f.write(self.request.files["file"][0]["body"])
                    
                self.flash(u"广告添加成功")
                self.redirect("/admin/ads")
                return
            except Exception, ex:
                self.flash(str(ex))
        else:
            self.flash(u"请选择图片")
        self.render('admin/addad.html')

@route(r'/admin/editad/(\d+)', name='admin_editad')
class EditAdHandler(AdminBaseHandler):
    
    def get(self, aid):
        aid = int(aid)
        
        try:
            ad = Ad.get(id = aid)
        except:
            self.flash("此广告不存在")
            self.redirect("/admin/ads")
            return
        
        self.render('admin/editad.html', ad = ad)
    
    def post(self, aid):
        aid = int(aid)
        
        try:
            ad = Ad.get(id = aid)
        except:
            self.flash("此广告不存在")
            self.redirect("/admin/ads")
            return
        
        url = self.get_argument("url", None)
        
        ad.url = url
        
        try:
            ad.validate()
            ad.save()
            
            if self.request.files:
                filename = str(ad.id) + ".jpg"
                with open('upload/ad/' + filename, "wb") as f:
                    f.write(self.request.files["file"][0]["body"])
                
            self.flash(u"广告修改成功")
            self.redirect("/admin/ads")
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/editad.html', ad = ad)

@route(r'/admin/delad/(\d+)', name='admin_delad')
class DelAdHandler(AdminBaseHandler):
    
    def get(self, aid):
        Ad.delete().where(Ad.id == aid).execute()
        self.flash(u"广告删除成功")
        self.redirect("/admin/ads")

@route(r'/admin/areas', name='admin_areas') #地区管理
class AreaHandler(AdminBaseHandler):
    
    def get(self):
        areas = []
        
        for area in Area.select().where(Area.pid == 0):
            areas.append(area)
            
            for carea in Area.select().where(Area.pid == area.id):
                areas.append(carea)
        
        self.render('admin/area.html', areas = areas)

@route(r'/admin/addarea', name='admin_addarea') #添加地区
class AddAreaHandler(AdminBaseHandler):
    
    def get(self):
        areas = Area.select().where(Area.pid == 0)
        self.render('admin/addarea.html', areas = areas)
    
    def post(self):
        areas = Area.select().where(Area.pid == 0)
        
        name = self.get_argument("name", None)
        pid = int(self.get_argument("pid", 0))
        
        area = Area()
        area.name = name
        area.pid = pid
        
        try:
            area.validate()
            area.save()
            self.redirect("/admin/areas")
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/addarea.html', areas = areas)

@route(r'/admin/editarea/(\d+)', name='admin_editarea') #编辑地区
class EditAreaHandler(AdminBaseHandler):
    
    def get(self, aid):
        areas = Area.select().where(Area.pid == 0)
        
        try:
            area = Area.get(id = aid)
        except:
            self.flash("此地区不存在")
            self.redirect("/admin/areas")
            return
        
        self.render('admin/editarea.html', area = area, areas = areas)
    
    def post(self, aid):
        areas = Area.select().where(Area.pid == 0)
        
        try:
            area = Area.get(id = aid)
        except:
            self.flash("此地区不存在")
            self.redirect("/admin/areas")
            return
        
        name = self.get_argument("name", None)
        
        area.name = name
        
        try:
            area.validate()
            area.save()
            self.redirect("/admin/areas")
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/editarea.html', area = area, areas = areas)
    
@route(r'/admin/delarea/(\d+)', name='admin_delarea') #删除地区
class DelAreaHandler(AdminBaseHandler):
    
    def get(self, aid):
        try:
            area = Area.get(id = aid)
            if Area.select().where(Area.pid == area.id).count() == 0:
                area.delete_instance()
                self.flash(u"地区删除成功")
            else:
                self.flash(u"请先删除子地区")
        except:
            pass
        
        self.redirect("/admin/areas")
    
@route(r'/admin/categorys', name='admin_categorys') #分类管理
class CategoryHandler(AdminBaseHandler):
    
    def get(self):
        categorys = self.get_categorys()
        self.render('admin/category.html', categorys = categorys)

@route(r'/admin/addcategory', name='admin_addcategory') #添加分类
class AddCategoryHandler(AdminBaseHandler):
    
    def get(self):
        self.render('admin/addcategory.html', maxorder = Category.maxorder())
    
    def post(self):
        name = self.get_argument("name", None)
        slug = self.get_argument("slug", None)
        order = int(self.get_argument("order", 1))
            
        category = Category()
        category.name = name
        category.slug = slug
        category.order = order
        
        try:
            category.validate()
            category.save()
            self.flash(u"分类%s添加成功" % name)
            self.redirect("/admin/addcategoryattr/" + str(category.id))
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/addcategory.html', maxorder = Category.maxorder())

@route(r'/admin/editcategory/(\d+)', name='admin_editcategory') #修改分类
class EditCategoryHandler(AdminBaseHandler):
    
    def get(self, cid):
        cid = int(cid)
        
        try:
            category = Category.get(id = cid)
        except:
            self.flash("此分类不存在")
            self.redirect("/admin/categorys")
            return
        
        self.render('admin/editcategory.html', category = category)
    
    def post(self, cid):
        
        try:
            category = Category.get(id = cid)
        except:
            self.flash("此分类不存在")
            self.redirect("/admin/categorys")
            return
        
        name = self.get_argument("name", None)
        slug = self.get_argument("slug", None)
        order = int(self.get_argument("order", 1))
        
        category.name = name
        category.slug = slug
        category.order = order
        
        try:
            category.validate()
            category.save()
            self.flash(u"分类%s修改成功" % name)
            self.redirect("/admin/categorys")
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/editcategory.html', category = category)

@route(r'/admin/delcategory/(\d+)', name='admin_delcategory') #删除分类
class DelCategoryHandler(AdminBaseHandler):
    
    def get(self, cid):
        Category.delete().where(Category.id == cid).execute()
        CategoryAttr.delete().where(CategoryAttr.cid == cid).execute()
        self.memcachedb.delete('categorys')
        self.flash(u"分类删除成功")
        self.redirect("/admin/categorys")

@route(r'/admin/categoryattrs/(\d+)', name='admin_categoryattrs') #分类属性管理
class CategoryAttrHandler(AdminBaseHandler):
    
    def get(self, cid):
        try:
            category = Category.get(id = cid)
        except:
            self.flash("此分类不存在")
            self.redirect("/admin/categorys")
            return
        
        categoryattrs = [categoryattr for categoryattr in CategoryAttr.select().where(CategoryAttr.cid == cid)]
        self.render('admin/categoryattr.html', category = category, categoryattrs = categoryattrs)

@route(r'/admin/addcategoryattr/(\d+)', name='admin_addcategoryattr') #添加分类属性
class AddCategoryAttrHandler(AdminBaseHandler):
    
    def get(self, cid):
        try:
            category = Category.get(id = cid)
        except:
            self.flash("此分类不存在")
            self.redirect("/admin/categorys")
            return
        
        self.render('admin/addcategoryattr.html', category = category, maxorder = CategoryAttr.maxorder(cid))
    
    def post(self, cid):
        try:
            category = Category.get(id = cid)
        except:
            self.flash("此分类不存在")
            self.redirect("/admin/categorys")
            return
        
        name = self.get_argument("name", None)
        dec = self.get_argument("dec", "")
        order = int(self.get_argument("order", 1))
            
        categoryattr = CategoryAttr()
        categoryattr.cid = cid
        categoryattr.name = name
        categoryattr.dec = dec
        categoryattr.order = order
        
        try:
            categoryattr.validate()
            categoryattr.save()
            self.flash(u"分类属性%s添加成功" % name)
            self.redirect("/admin/categoryattrs/%d" % int(cid))
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/addcategoryattr.html', category = category, maxorder = CategoryAttr.maxorder(cid))

@route(r'/admin/editcategoryattr/(\d+)', name='admin_editcategoryattr') #修改分类属性
class EditCategoryAttrHandler(AdminBaseHandler):
    
    def get(self, caid):
        try:
            categoryattr = CategoryAttr.get(id = caid)
            category = Category.get(id = categoryattr.cid)
        except:
            self.flash("此分类属性不存在")
            self.redirect("/admin/categorys")
            return
        
        self.render('admin/editcategoryattr.html', category = category, categoryattr = categoryattr)
    
    def post(self, caid):
        try:
            categoryattr = CategoryAttr.get(id = caid)
            category = Category.get(id = categoryattr.cid)
        except:
            self.flash("此分类属性不存在")
            self.redirect("/admin/categorys")
            return
        
        name = self.get_argument("name", None)
        dec = self.get_argument("dec", "")
        order = int(self.get_argument("order", 1))
            
        categoryattr.name = name
        categoryattr.dec = dec
        categoryattr.order = order
        
        try:
            categoryattr.validate()
            categoryattr.save()
            self.flash(u"分类属性%s修改成功" % name)
            self.redirect("/admin/categoryattrs/%d" % int(categoryattr.cid))
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/editcategoryattr.html', category = category, categoryattr = categoryattr)

@route(r'/admin/delcategoryattr/(\d+)', name='admin_delcategoryattr') #删除分类
class DelCategoryAttrHandler(AdminBaseHandler):
    
    def get(self, caid):
        CategoryAttr.delete().where(CategoryAttr.id == caid).execute()
        self.flash(u"分类删除成功")
        self.redirect(self.request.headers["Referer"])

@route(r'/admin/shops', name='admin_shops') #商品管理
class ShopHandler(AdminBaseHandler):
    
    def get(self):
        page = int(self.get_argument("page", 1))
        cid = int(self.get_argument("cid", 0))
        status = int(self.get_argument("status", 0))
        pagesize = self.settings['admin_pagesize']
        
        categorys = self.get_categorys()
        
        sq = Shop.select()
        
        if cid > 0:
            sq = sq.where(Shop.cid == cid)
        
        if status > 0:
            sq = sq.where(Shop.status == status)
        
        total = sq.count()
        shops = sq.paginate(page, pagesize)
        
        self.render('admin/shop.html', categorys = categorys, shops = shops, total = total, page = page, pagesize = pagesize)

@route(r'/admin/addshop', name='admin_addshop') #添加商品
class AddShopHandler(AdminBaseHandler):
    
    def get(self):
        categorys = self.get_categorys()
        self.render('admin/addshop.html', categorys = categorys)

@route(r'/admin/addshop/(\d+)', name='admin_addcshop') #添加商品
class AddCShopHandler(AdminBaseHandler):
    
    def get(self, cid):
        try:
            category = Category.get(id = cid)
        except:
            self.flash("此分类不存在")
            self.redirect("/admin/addshop")
            return
        
        categoryattrs = CategoryAttr.select().where(CategoryAttr.cid == cid)
        self.render('admin/addcshop.html', category = category, categoryattrs = categoryattrs)
    
    def post(self, cid):
        try:
            category = Category.get(id = cid)
        except:
            self.flash("此分类不存在")
            self.redirect("/admin/addshop")
            return
        
        categoryattrs = CategoryAttr.select().where(CategoryAttr.cid == cid)
        
        cover = self.get_argument("cover", None)
        pics = self.get_argument("pics", None)
        name = self.get_argument("name", None)
        ename = self.get_argument("ename", None)
        price = str(float(str(self.get_argument("price", 0.0))))
        level = int(self.get_argument("level", 3))
        resume = self.get_argument("resume", "")
        intro = self.get_argument("intro", "")
        prompt = self.get_argument("prompt", "")
        views = int(self.get_argument("views", 0))
        
        try:
            shop = Shop()
            shop.name = name
            shop.ename = ename
            shop.cid = cid
            shop.level = level
            shop.resume = resume
            shop.intro = intro
            shop.prompt = prompt
            shop.price = price
            shop.views = views
            
            args = {}
            for categoryattr in categoryattrs:
                caid = str(categoryattr.id)
                args['attr_' + caid] = self.get_argument('attr_' + caid, '')
            
            shop.args = simplejson.dumps(args)
            
            if pics:
                pics = pics.split(',')
                pics = [pic.replace('/upload/', '') for pic in pics]
                
                if not cover:
                    cover = pics[0]
            
            if not cover:
                cover = ''
            
            shop.cover = cover.replace('/upload/', '')
            shop.validate()
            shop.save()
            
            if isinstance(pics, list):
                for pic in pics:
                    shoppic = ShopPic()
                    shoppic.sid = shop.id
                    shoppic.path = pic
                    shoppic.save()
            
            self.flash(u"添加商品%s成功" % name, 'ok')
            if category.id == 2:
                self.redirect("/admin/shops")
            else:
                self.redirect("/admin/addshopattr/" + str(shop.id))
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/addcshop.html', category = category, categoryattrs = categoryattrs)

@route(r'/admin/editshop/(\d+)', name='admin_editshop') #修改商品
class EditShopHandler(AdminBaseHandler):
    
    def get(self, sid):
        try:
            shop = Shop.get(id = sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/addshop")
            return
        
        try:
            category = Category.get(id = shop.cid)
        except:
            pass
        
        categoryattrs = CategoryAttr.select().where(CategoryAttr.cid == shop.cid)
        
        pics = [shoppic.path for shoppic in ShopPic.select().where(ShopPic.sid == sid)]
        shop.args = simplejson.loads(shop.args)
        
        self.render('admin/editshop.html', shop = shop, pics = pics, category = category, categoryattrs = categoryattrs)
    
    def post(self, sid):
        try:
            shop = Shop.get(id = sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/addshop")
            return
        
        try:
            category = Category.get(id = shop.cid)
        except:
            pass
        
        categoryattrs = CategoryAttr.select().where(CategoryAttr.cid == shop.cid)
        
        opics = [shoppic.path for shoppic in ShopPic.select().where(ShopPic.sid == sid)]
        
        cover = self.get_argument("cover", None)
        pics = self.get_argument("pics", None)
        name = self.get_argument("name", None)
        ename = self.get_argument("ename", None)
        price = self.get_argument("price", 0.0)
        views = int(self.get_argument("views", 0))
        
        if category.id == 2:
            price = str(float(price))
        
        level = int(self.get_argument("level", 3))
        resume = self.get_argument("resume", "")
        intro = self.get_argument("intro", "")
        prompt = self.get_argument("prompt", "")
        
        try:
            shop.name = name
            shop.ename = ename
            shop.level = level
            shop.resume = resume
            shop.intro = intro
            shop.prompt = prompt
            shop.price = price
            shop.views = views
            
            args = {}
            for categoryattr in categoryattrs:
                caid = str(categoryattr.id)
                args['attr_' + caid] = self.get_argument('attr_' + caid, '')
            
            shop.args = simplejson.dumps(args)
            
            if pics:
                pics = pics.split(',')
                pics = [pic.replace('/upload/', '') for pic in pics]
                if not cover:
                    cover = pics[0]
            
            if not cover:
                cover = ''
            
            shop.cover = cover.replace('/upload/', '')
            shop.validate()
            shop.save()
            
            if isinstance(pics, list):
                for pic in pics:
                    if pic not in opics:
                        shoppic = ShopPic()
                        shoppic.sid = shop.id
                        shoppic.path = pic
                        shoppic.save()
                
                for pic in opics:
                    if pic not in pics:
                        ShopPic.delete().where(ShopPic.path == pic).execute()
            
            self.flash(u"修改商品%s成功" % name, 'ok')
            self.redirect("/admin/shops")
            return
        except Exception, ex:
            shop.args = simplejson.loads(shop.args)
            self.flash(str(ex))
        
        self.render('admin/editshop.html', shop = shop, pics = opics, category = category, categoryattrs = categoryattrs)

@route(r'/admin/recommshop/(\d+)', name='admin_recommshop') #推荐商品
class RecommShopHandler(AdminBaseHandler):
    
    def get(self, sid):
        try:
            shop = Shop.get(id = sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/addshop")
            return
        
        if shop.status == 1:
            shop.status = 0
        else:
            shop.status = 1
        
        shop.save()
        
        self.flash(u"推荐商品%s成功" % shop.name, 'ok')
        self.redirect("/admin/shops")

@route(r'/admin/delshop/(\d+)', name='admin_delshop') #删除商品
class DelShopHandler(AdminBaseHandler):
    
    def get(self, sid):
        #Shop.delete().where(Shop.id == sid).execute()
        #ShopPic.delete().where(ShopPic.sid == sid).execute()
        #ShopAttr.delete().where(ShopAttr.sid == sid).execute()
        
        try:
            shop = Shop.get(id = sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/addshop")
            return
        
        if shop.status == 9:
            shop.status = 0
        else:
            shop.status = 9
        shop.save()
        
        self.flash(u"商品操作成功")
        self.redirect(self.request.headers["Referer"])

@route(r'/admin/shopattrs/(\d+)', name='admin_shopattrs') #商品规格和价格
class ShopAttrHandler(AdminBaseHandler):
    
    def get(self, sid):
        try:
            shop = Shop.get(id = sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/addshop")
            return
        
        shopattrs = [shopattr for shopattr in ShopAttr.select().where(ShopAttr.sid == sid)]
        self.render('admin/shopattr.html', shop = shop, shopattrs = shopattrs)

@route(r'/admin/addshopattr/(\d+)', name='admin_addshopattrs') #添加商品规格和价格
class AddShopAttrHandler(AdminBaseHandler):
    
    def get(self, sid):
        try:
            shop = Shop.get(id = sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/shops")
            return
        
        self.render('admin/addshopattr.html', shop = shop, maxorder = ShopAttr.maxorder(sid))
    
    def post(self, sid):
        try:
            shop = Shop.get(id = sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/shops")
            return
        
        name = self.get_argument("name", None)
        price = float(str(self.get_argument("price", 0.0)))
        order = int(self.get_argument("order", 1))

        shopattr = ShopAttr()
        shopattr.sid = sid
        shopattr.name = name
        shopattr.price = price
        shopattr.order = order

        try:
            shopattr.validate()
            shopattr.save()
            self.flash(u"规格%s添加成功" % name)
            self.redirect("/admin/shopattrs/%d" % int(sid) )
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/addshopattr.html', shop = shop, maxorder = ShopAttr.maxorder(sid))

@route(r'/admin/editshopattr/(\d+)', name='admin_editshopattrs') #添加商品规格和价格
class EditShopAttrHandler(AdminBaseHandler):
    
    def get(self, said):
        try:
            shopattr = ShopAttr.get(id = said)
            shop = Shop.get(id = shopattr.sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/shops")
            return
        
        self.render('admin/editshopattr.html', shop = shop, shopattr = shopattr)
    
    def post(self, said):
        try:
            shopattr = ShopAttr.get(id = said)
            shop = Shop.get(id = shopattr.sid)
        except:
            self.flash("此商品不存在")
            self.redirect("/admin/shops")
            return
        
        name = self.get_argument("name", None)
        price = float(str(self.get_argument("price", 0.0)))
        order = int(self.get_argument("order", 1))

        shopattr.name = name
        shopattr.price = price
        shopattr.order = order

        try:
            shopattr.validate()
            shopattr.save()
            self.flash(u"规格%s修改成功" % name)
            self.redirect("/admin/shopattrs/%d" % int(shopattr.sid) )
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/editshopattr.html', shop = shop, shopattr = shopattr)

@route(r'/admin/delshopattr/(\d+)', name='admin_delshopattrs') #添加商品规格和价格
class DelShopAttrHandler(AdminBaseHandler):
    
    def get(self, said):
        ShopAttr.delete().where(ShopAttr.id == said).execute()
        self.flash(u"规格删除成功")
        self.redirect(self.request.headers["Referer"])

@route(r'/admin/orders', name='admin_orders') #订单管理
class OrderHandler(AdminBaseHandler):
    
    def get(self):
        status = self.get_argument("status", None)
        ft = (Order.status >= 0)
        if status:
            ft = ft & (Order.status == status)
        
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        oq = Order.select().where(ft)
        total = oq.count()
                
        orders = []
        for order in oq.paginate(page, pagesize).order_by(Order.ordered.desc()).dicts():
            order['orderitems'] = []
            try:
                order['ua'] = UserAddr.get(id = order['uaid'])
            except:
                order['ua'] = UserAddr()
            
            try:
                order['distr'] = Distribution.get(id = order['distrid'])
            except:
                order['distr'] = Distribution()
                
            for orderitem in OrderItem.select().where(OrderItem.oid == order['id']).dicts():
                
                try:
                    orderitem['shop'] = Shop.get(id = orderitem['sid'])
                    if orderitem['said'] > 0:
                        orderitem['shopattr'] = ShopAttr.get(id = orderitem['said'])
                    
                    order['orderitems'].append(orderitem)
                except:
                    orderitem['shop'] = Shop()
            
            if order['orderitems']:
                orders.append(order)
        
        self.render('admin/order.html', orders = orders, total = total, page = page, pagesize = pagesize)

@route(r'/admin/changeorder/(\d+)', name='admin_changeorder') #修改订单状态
class ChangeOrderHandler(AdminBaseHandler):
    
    def get(self, oid):
        try:
            order = Order.get(id = oid)
        except:
            pass
        
        self.render("admin/changeorder.html", order = order)
    
    def post(self, oid):
        status = int(self.get_argument("status", 0))
        
        Order.update(status = status).where(Order.id == oid).execute()
        self.flash("修改成功")
        self.redirect("/admin/orders")

@route(r'/admin/pages', name='admin_pages') #栏目页管理
class PageHandler(AdminBaseHandler):
    
    def get(self):
        
        pages = [page for page in Page.select()]
        self.render('admin/page.html', pages = pages)

@route(r'/admin/addpage', name='admin_addpage') #添加栏目页
class AddPageHandler(AdminBaseHandler):
    
    def get(self):
        self.render('admin/addpage.html')
    
    def post(self):
        name = self.get_argument("name", None)
        slug = self.get_argument("slug", None)
        content = self.get_argument("content", "")
        template = self.get_argument("template", "staticpage.html")
        
        page = Page()
        page.name = name
        page.slug = slug
        page.content = content
        page.template = template
        
        try:
            page.validate()
            page.save()
            self.flash(u"栏目%s添加成功" % name)
            self.redirect("/admin/pages")
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/addpage.html')

@route(r'/admin/editpage/(\d+)', name='admin_editpage') #修改栏目页
class EditPageHandler(AdminBaseHandler):
    
    def get(self, pid):
        try:
            page = Page.get(id = pid)
        except:
            self.flash("此栏目不存在")
            self.redirect("/admin/pages")
            return
        self.render('admin/editpage.html', page = page)
    
    def post(self, pid):
        
        try:
            page = Page.get(id = pid)
        except:
            self.flash("此栏目不存在")
            self.redirect("/admin/pages")
            return
        
        name = self.get_argument("name", None)
        slug = self.get_argument("slug", None)
        content = self.get_argument("content", "")
        template = self.get_argument("template", "staticpage.html")
        
        page.name = name
        page.slug = slug
        page.content = content
        page.template = template
        
        try:
            page.validate()
            page.save()
            self.flash(u"栏目%s修改成功" % name)
            self.redirect("/admin/pages")
            return
        except Exception, ex:
            self.flash(str(ex))
        
        self.render('admin/editpage.html', page = page)

@route(r'/admin/delpage/(\d+)', name='admin_delpage') #添加商品规格和价格
class DelPageHandler(AdminBaseHandler):
    
    def get(self, pid):
        Page.delete().where(Page.id == pid).execute()
        self.flash(u"栏目删除成功")
        self.redirect(self.request.headers["Referer"])

@route(r'/admin/applys', name='admin_applys') #静态页面管理
class ApplyHandler(AdminBaseHandler):
    
    def get(self):
        keyword = self.get_argument("keyword", None)
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        aq = Apply.select()
        
        if keyword:
            keyword = keyword + '%'
            aq = aq.where((Apply.coname % keyword) | (Apply.mobile % keyword))
        
        total = aq.count()
        
        applys = aq.paginate(page, pagesize)
        
        self.render('admin/apply.html', applys = applys, total = total, page = page, pagesize = pagesize)

@route(r'/admin/distributions', name='admin_distributions')
class DistributionHandler(AdminBaseHandler):
    
    def get(self):
        distributions = self.get_distributions()
        self.render('admin/distribution.html', distributions = distributions.values())

@route(r'/admin/adddistribution', name='admin_adddistribution')
class AddDistributionHandler(AdminBaseHandler):
    
    def get(self):
        distributions = self.get_distributions()
        self.render('admin/adddistribution.html', distributions = distributions.values())
        
    def post(self):
        pdid = int(self.get_argument('pdid', 0))
        name = self.get_argument('name', None)
        price = float(str(self.get_argument("price", 0.0)))
        content = self.get_argument('content', '')
        
        distribution = Distribution()
        distribution.pdid = pdid
        distribution.name = name
        distribution.price = price
        distribution.content = content
        
        try:
            distribution.validate()
            distribution.save()
            self.flash(u"配送方式%s添加成功" % name)
            self.redirect("/admin/distributions")
            return
        except Exception, ex:
            self.flash(str(ex))
            
        distributions = self.get_distributions()
        
        self.render('admin/adddistribution.html', distributions = distributions.values())

@route(r'/admin/editdistribution/(\d+)', name='admin_editdistribution')
class EditDistributionHandler(AdminBaseHandler):
    
    def get(self, did):
        try:
            distribution = Distribution.get(id = did)
        except:
            self.flash("此配送方式不存在")
            self.redirect("/admin/distributions")
            return
        
        distributions = self.get_distributions()
        self.render('admin/editdistribution.html', distribution = distribution, distributions = distributions.values())
        
    def post(self, did):
        try:
            distribution = Distribution.get(id = did)
        except:
            self.flash("此配送方式不存在")
            self.redirect("/admin/distributions")
            return
        
        pdid = int(self.get_argument('pdid', 0))
        name = self.get_argument('name', None)
        price = float(str(self.get_argument("price", 0.0)))
        content = self.get_argument('content', '')
        
        distribution.pdid = pdid
        distribution.name = name
        distribution.price = price
        distribution.content = content
        
        try:
            distribution.validate()
            distribution.save()
            self.flash(u"配送方式%s修改成功" % name)
            self.redirect("/admin/distributions")
            return
        except Exception, ex:
            self.flash(str(ex))
            
        distributions = self.get_distributions()
        
        self.render('admin/editdistribution.html', distribution = distribution, distributions = distributions.values())

@route(r'/admin/deldistribution/(\d+)', name='admin_deldistribution')
class DelDistributionHandler(AdminBaseHandler):
    
    def get(self, did):
        Distribution.delete().where(Distribution.id == did).execute()
        self.memcachedb.remove('distributions')
        self.flash(u"栏目配送方式成功")
        self.redirect(self.request.headers["Referer"])

@route(r'/admin/consults', name='admin_consults')
class ConsultHandler(AdminBaseHandler):
    
    def get(self):
        page = int(self.get_argument("page", 1))
        pagesize = self.settings['admin_pagesize']
        
        cq = Consult.select()
        total = cq.count()
        consults = []
        
        for consult in cq.order_by(Consult.posted.desc(), Consult.replyed.asc()).paginate(page, pagesize).dicts():
            try:
                shop = Shop.get(id = consult['sid'])
            except:
                shop = Shop
            consult['shop'] = shop
            consults.append(consult)
        
        self.render('admin/consult.html', consults = consults, total = total, page = page, pagesize = pagesize)

@route(r'/admin/replyconsult/(\d+)', name='admin_replyconsult')
class ReplyConsultHandler(AdminBaseHandler):
    
    def post(self, cid):
        try:
            consult = Consult.get(id = cid)
            reply = self.get_argument('reply', '')
    
            if (reply != ""):
                consult.reply = reply
                consult.replyed = int(time.time())
                consult.save()
        except:
            pass
        
        self.flash(u"回复成功")
        self.redirect(self.request.headers["Referer"])

@route(r'/admin/password', name='admin_password') #修改密码
class PasswordHandler(AdminBaseHandler):
    
    def get(self):
        self.render('admin/password.html')
    
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
        
        self.render('admin/password.html')