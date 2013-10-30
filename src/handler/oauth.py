#!/usr/bin/env python
#coding=utf8

import logging
import tornado.web
from tornado import gen
from lib.route import route
from lib.oauth import WeiboMixin
from lib.alipay import Alipay
from handler import BaseHandler
from model import Oauth, User

@route(r'/oauth/redirect', name='oauth_redirect') #跳转
class AuthRedirectHandler(BaseHandler, WeiboMixin):
    
    def get(self):
        next_url = self.get_cookie("next", "/")
        
        if 'oauth' in self.session:
            oauth = self.session['oauth']
            
            try:
                oauth = Oauth.get(Oauth.src == oauth['src'],  Oauth.openid == oauth['id'])
                user = User.get(User.id == oauth.uid)
                
                del self.session["oauth"]
                self.session['user'] = user
                self.session.save()
                self.redirect(next_url)
                return
            except:
                pass
            
            self.render('site/oauth.html', oauth = oauth, next = next_url)

@route(r'/oauth/weibo', name='oauth_weibo') #新浪微博
class WeiboAuthHandler(BaseHandler, WeiboMixin):
    
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        
        if not self.get_cookie("next", None):
            self.set_cookie("next", self.next_url)
        
        if self.get_argument('code', None):
            user = yield self.get_authenticated_user(
                redirect_uri=self.settings['weibo_redirect'],
                client_id=self.settings['weibo_key'],
                client_secret=self.settings['weibo_secret'],
                code=self.get_argument('code'))
            
            if user:
                user['src'] = 'weibo'
                self.session['oauth'] = user
                self.session.save()
                self.redirect("/oauth/redirect")
            else:
                logging.error("can not oauth2")
        else:
            self.authorize_redirect(
                redirect_uri=self.settings['weibo_redirect'],
                client_id=self.settings['weibo_key']
                )

@route(r'/oauth/alipay', name='oauth_alipay')
class AlipayAuthHandler(BaseHandler):
    
    def get(self):
        if not self.get_cookie("next", None):
            self.set_cookie("next", self.next_url)
                
        alipay = Alipay(**self.settings)
        self.redirect(alipay.create_authurl())

@route(r'/oauth/alipay_return', name='oauth_ailpay_return')
class AlipayReturnHandler(BaseHandler):
    
    def get(self):  
        real_name = self.get_argument("real_name", None)
        user_id = self.get_argument("user_id", None)
        
        alipay = Alipay(**self.settings)
        
        params = {}
        ks = self.request.arguments.keys()
        
        for k in ks:
            params[k] = self.get_argument(k)
        
        if alipay.notify_verify(params):
            user = {}
            user['id'] = user_id
            user['screen_name'] = real_name
            user['profile_image_url'] = ''
            user['src'] = 'alipay'
            
            self.session['oauth'] = user
            self.session.save()
            
            self.redirect("/oauth/redirect")
            return
        else:
            self.flash("支付宝登录失败")
        
        self.redirect("/signin")