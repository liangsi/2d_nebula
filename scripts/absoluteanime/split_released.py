#
# some data in db:
# [u'13 half-hour episodes, 24 fifteen-minute episodes, 3 specials']
#
# want 
# [u'13 half-hour episodes', u'24 fifteen-minute episodes', u'3 specials']
from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime

for one in absoluteanime.find():
    if one['jp_info'].get('released', None):
        released = one['jp_info']['released']
        releases = []
        
        for n in released:
            releases.extend(
                [y for y in [x.strip() for x in n.split(',')] if y])

        absoluteanime.update(
        {'url': one['url']},
        {'$set':{
            'jp_info.released': releases,
        }})