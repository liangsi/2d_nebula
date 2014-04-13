import web
import config

view = web.template.render('app/views/', cache=config.cache)

class index:
    def GET(self):
        keyword = ''
        return config.base.layout(view.search(keyword), title='Search')
        #return view.search(keyword)

