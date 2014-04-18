import re

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime
absoluteanime_0418 = db.absoluteanime_0418


def get_type(text):
    if 'TV' in text.upper():
        return 'TV'
    elif 'MOVIE' in text.upper():
        return 'Movie'
    elif 'OVA' in text.upper():
        return 'OVA'
    elif 'ONA' in text.upper():
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


def remove_key(d):
    r = dict(d)
    del r['_id']
    return r

for one in absoluteanime.find():
    released_type = ''
    released_episodes = 0

    if 'released' in one['jp_info']:
        for release in one['jp_info']['released']:
            anime_obj = remove_key(one)

            anime_obj['jp_info']['released_type'] = get_type(release)
            anime_obj['jp_info']['released_episodes'] = get_episodes_num(release)
            
            absoluteanime_0418.insert(anime_obj)

