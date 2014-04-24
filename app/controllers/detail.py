# -*- coding: utf-8 -*-
import web
import config
from app.model import db
from app.controllers import twitter

view = web.template.render('app/views/', cache=config.cache)

class detail:
    def GET(self):
        id = web.input().get('id','')
        anime = db.Database()
        (content,related_animes) = anime.get_details(id)
        t = twitter.Twitter()
        content['twitter'] = t.detail(content,5)
        print len(content['twitter'])
        title = content['title']
        return config.base.layout(view.detail(content), 'Detail | ' + title)


