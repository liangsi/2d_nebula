# -*- coding: utf-8 -*-
import web
import config

from app.model import db
from app.controllers import twitter

view = web.template.render('app/views/', cache=config.cache)

class result:
    def GET(self):
		# keyword in get
        keyword = web.input().get('keyword','')
        content = {}
        ## TODO anime_list = db.find(keyword)
        
        if keyword != '':
            anime = db.Database()
            anime_list = anime.search(keyword)
            content['anime_list'] = anime_list

            t = twitter.Twitter()
            content['twitter'] = t.search(keyword)
        else:
            content['twitter'] = []
            content['anime_list'] = []

        return config.base.layout(view.search(content), title='Search Results')

