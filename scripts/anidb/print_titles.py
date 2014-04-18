from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

# cat titles.txt | egrep '\([0-9]{4}\)'
for anime in anidb.find():
	print anime['Main_Title'], anime['Year']