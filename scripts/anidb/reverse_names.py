from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

def reverse_words(name):
    return ' '.join(name.split(' ')[::-1]) 

for anime in anidb.find():
    url = anime['url'] 
    creators = anime.get('staffs', []).get('Original Work', [])
    directors = anime.get('staffs', []).get('Direction', [])

    reversed_creators = []
    reversed_directors = []

    for name in creators:
        reversed_creators.append(reverse_words(name))

    for name in directors:
        reversed_directors.append(reverse_words(name))

    anidb.update(
        {'url':url},
        {'$set':{
            'staffs.Original Work':reversed_creators,
            'staffs.Direction':reversed_directors
        }})