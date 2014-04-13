import web

# connect to the database
#########TODO config db

web.webapi.internalerror = web.debugerror
#middleware = [web.reloader]

# set template caching to false for debugging purposes
cache = False

# set our global base template
base = web.template.render('app/views/base/', cache=cache)

web.template.Template.globals.update(dict(
  datestr = web.datestr,
))