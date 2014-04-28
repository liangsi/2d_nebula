import web
import config

view = web.template.render('app/views/', cache=config.cache)

class index:
    def GET(self):
        # keyword = ''
        return view.index()
        #return view.search(keyword)

