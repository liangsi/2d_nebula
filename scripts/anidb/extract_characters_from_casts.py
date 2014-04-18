from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

for anime in anidb.find():
    url = anime['url']
    casts = anime.get('casts', [])

    chars = []

    for cast in casts:
        char = {}
        char['name'] = cast['char']
        char['url'] = cast['char_link']

        chars.append(char)

    anidb.update(
        {'url': url},
        {'$set' : {
            'characters' : chars
        }})
