import re

from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

for anime in anidb.find({'Main_Title': {'$regex': '\([0-9]{4}\)', '$options': 'i'}}):
    url = anime['url']
    title = anime['Main_Title']

    title = re.sub('\([0-9]{4}\)', '', title).strip().replace('  ', '')

    anidb.update({'url': url}, {'$set': {'Main_Title': title}})
