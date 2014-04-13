#! /usr/bin/env python

import web
import config
import app.controllers

urls = (
    #pages
    '/',                                    'app.controllers.base.index',
    '/search_result/',                      'app.controllers.search.result',
    '/detail/',                              'app.controllers.detail.detail',
)

if __name__ == "__main__":
    app = web.application(urls, globals())  
    app.run()  
