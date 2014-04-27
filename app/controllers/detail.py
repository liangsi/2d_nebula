# -*- coding: utf-8 -*-
import web
import config
import random
from app.model import db
from app.controllers import twitter
from app.controllers import amazon_api
from app.controllers import flickr_api

view = web.template.render('app/views/', cache=config.cache)

class detail:
    def GET(self):
        id = web.input().get('id','')
        anime = db.Database()
        (content,related_animes) = anime.get_details(id)
        t = twitter.Twitter()
        amazon = amazon_api.AmazonDvd()
        flickr = flickr_api.Flickr()
        content['amazon'] = amazon.find_product(content['title'],content['directors'][0])
        (isTitle,c,content['twitter']) = t.detail(content,5)

        # something disgusting about the keywords... G.... I don't want to talk about it...
        if(isTitle):
            if(len(c) == 1):
                keywords = (content['title'])
            else:
                keywords = ' '.join(c)

        content['related_animes'] = [ (i['image_file'],i['oid']) for i in related_animes]

        j = 0
        f = []
        while(len(f)<9 and j<len(c)):
                if(not isTitle):
                    keywords = (random.choice(c)+' '+content['title'])
                    j = j+1
                f.extend(flickr.get_photos(keywords))

        content['flickr'] = f[:8]

        title = content['title']
        return config.base.layout(view.detail(content), 'Detail | ' + title)


