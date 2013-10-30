#!/usr/bin/env python
#coding=utf8

import urllib
from tornado.web import RequestHandler
from lib.session import Session
from lib.mixin import FlashMessagesMixin
from model import Category, Distribution

class BaseHandler(RequestHandler, FlashMessagesMixin):
    
    def set_default_headers(self):
        self.clear_header('Server')
    
    def render_string(self, template_name, **context):
        context.update({
            'xsrf': self.xsrf_form_html,
            'module': self.ui.modules,
            'request': self.request,
            'user': self.current_user,
            'handler': self,}
        )

        return self._jinja_render(path = self.get_template_path(),filename = template_name,
            auto_reload = self.settings['debug'], **context)

    def _jinja_render(self,path,filename, **context):
        template = self.application.jinja_env.get_template(filename,parent=path)
        return template.render(**context)
    
    @property
    def is_xhr(self):
        return self.request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest'
    
    @property
    def memcachedb(self):
        return self.application.memcachedb
    
    @property
    def session(self):
        if hasattr(self, '_session'):
            return self._session
        else:
            sessionid = self.get_secure_cookie('sid')
            self._session = Session(self.application.session_store, sessionid, expires_days=1)
            if not sessionid:
                self.set_secure_cookie('sid', self._session.id, expires_days=1)
            return self._session
    
    def get_current_user(self):
        return self.session['user'] if 'user' in self.session else None
    
    @property
    def next_url(self):
        return self.get_argument("next", "/")
    
    def get_categorys(self):
        categorys = self.memcachedb.get('categorys')
        
        if not categorys:
            categorys = [category for category in Category.select()]
            self.memcachedb.set('categorys', categorys, 86400)
        
        return categorys
    
    def get_distributions(self):
        distributions = self.memcachedb.get('distributions')
        
        if not distributions:
            distributions = {}
            
            for distribution in Distribution.select().dicts():
                if distribution['pdid'] == 0:
                    distribution['list'] = []
                    distributions[distribution['id']] = distribution
                else:
                    distributions[distribution['pdid']]['list'].append(distribution)
            
            self.memcachedb.replace('distributions', distributions, 86400)
        return distributions

class AdminBaseHandler(BaseHandler):

    def prepare(self):
        if not self.current_user:
            url = self.get_login_url()
            if "?" not in url:
                url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
            self.redirect(url)
        elif self.current_user.group != 9:
            self.redirect("/")
        
        super(AdminBaseHandler, self).prepare()

class UserBaseHandler(BaseHandler):
    
    def prepare(self):
        if not self.current_user:
            url = self.get_login_url()
            if "?" not in url:
                url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
            self.redirect(url)
        
        super(UserBaseHandler, self).prepare()