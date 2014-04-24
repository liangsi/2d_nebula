# -*- coding: utf-8 -*-
import web
import config
from app.model import db
from app.controllers import twitter
from app.controllers import amazon_api

view = web.template.render('app/views/', cache=config.cache)

class detail:
    def GET(self):
        id = web.input().get('id','')
        anime = db.Database()
        (content,related_animes) = anime.get_details(id)
        t = twitter.Twitter()
        amazon = amazon_api.AmazonDvd()
        content['amazon'] = amazon.find_product(content['title'],content['directors'][0])
        print content['amazon'][0]
        content['twitter'] = t.detail(content,5)
        title = content['title']
        return config.base.layout(view.detail(content), 'Detail | ' + title)


