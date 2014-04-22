import urllib
import os

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.anime
integrated = db.integrated_0420

for obj in integrated.find():
    oid = obj['_id']
    
    for num, url in enumerate(obj['images']):
        ext = url.split('.')[-1]
        file_name = '%s-%d.%s' % (oid, num, ext)
        try:
            f = open(file_name, 'wb')
            f.write(urllib.urlopen(url).read())
            f.close()
        except Exception, e:
            f.close()
            os.remove(file_name)
            raise e