#!/usr/bin/env python
#coding=utf8

from tornado.web import UIModule

class Paginate(UIModule):
    def render(self, total, pagesize, page):
        uri = self.request.uri.split('?')
        
        if len(uri) > 1:
            args = "&".join(filter(lambda ai: not ai.startswith('page'), uri[1].split('&')))
            if args != "":
                uri = "?".join([uri[0], args])    
        
        if isinstance(uri, list):
            uri = uri[0]
        
        pages = 1
        if total > 0:
            pages = total / pagesize
        page = int(page)

        if total % pagesize > 0:
            pages = pages + 1

        if uri.find("?") > -1:
            uri = uri + "&page="
        else:
            uri = uri + "?page="
            
        prepage = 1
        if page - 1 > 1:
            prepage = page - 1

        nextpage = pages
        if page + 1 < pages:
            nextpage = page + 1
        
        return self.render_string('layout/page.html', total = total, pagesize = pagesize, pages = pages, page = page, prepage = prepage, nextpage = nextpage, url = uri);