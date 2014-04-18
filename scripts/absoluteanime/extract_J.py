import json
import codecs

from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime

j = []

for anime in absoluteanime.find({"jp_info.title": {"$regex": '^J.*', "$options": 'i'}}):
    anime.pop("_id")
    j.append(anime)

with codecs.open('j_anime.json', 'w', 'utf-8') as f:
    f.write(json.dumps(j, indent=4, sort_keys=True))
