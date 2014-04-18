#
# some data in db:
# "creator" : [
#		"Hajime Yatate",
#		"Yoshiyuki Tomino",
#		"Yoshiyuki Tomino, Hajime Yatate"
#	],
#
from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime

for one in absoluteanime.find():
    if one['jp_info'].get('creator', None):
        names = one['jp_info']['creator']
        creators = []
        
        for n in names:
            creators.extend(
                [y for y in [x.strip() for x in n.split(',')] if y])

        absoluteanime.update(
        {'url': one['url']},
        {'$set':{
            'jp_info.creator': creators,
        }})

    if one['jp_info'].get('director', None):
        names = one['jp_info']['director']
        directors = []

        for n in names:
            directors.extend(
                [y for y in [x.strip() for x in n.split(',')] if y])

        absoluteanime.update(
        {'url': one['url']},
        {'$set':{
            'jp_info.director': directors,
        }})