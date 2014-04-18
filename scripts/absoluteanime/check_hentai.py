import json
import codecs

from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime

for anime in absoluteanime.find({"jp_info.genre": {"$regex" : 'Hentai', "$options" : 'i'}}):
	url = anime['url']
	absoluteanime.remove({"url": url})
	print url