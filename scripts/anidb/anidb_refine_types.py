import re

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

def get_type(text):
    if 'TV' in text.upper():
        return 'TV'
    elif 'MOVIE' in text.upper():
        return 'Movie'
    elif 'OVA' in text.upper():
        return 'OVA'
    elif 'WEB' in text.upper():
        return 'Web'
    elif 'MUSIC VIDEO' in text.upper():
        return 'Music Video'
    else:
        return None

def get_episodes_num(text):
    o = re.search(r'[0-9]+', text)
    if o:
        return int(o.group())
    else:
        return None

for one in anidb.find():
    released_type = ''
    released_episodes = 0
    
    if 'Type' in one:
        released_type = get_type(one['Type'])
        released_episodes = get_episodes_num(one['Type'])
        
        anidb.update(
        {'url': one['url']}, 
        {'$set': {
            'released_type' : released_type,
            'released_episodes' : released_episodes
            },
         '$unset': {
            'Type' : ""
            }
        })