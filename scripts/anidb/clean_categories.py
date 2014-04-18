from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

for anime in anidb.find():
    url = anime['url'] 
    categories = anime.get('Categories', [])

    if isinstance(categories, list):
        categories = categories[:-1]
        anidb.update(
            {'url': url}, 
            {
                '$set': {
                    'Categories': categories
                    }
            })
    else:
        anidb.update(
            {'url': url}, 
            {
                '$unset': {
                    'Categories': ""
                    }
            })