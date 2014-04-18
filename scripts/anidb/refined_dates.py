import csv

from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

dates_reader = csv.reader(
    open('anidb_dates_refined.csv', 'rU'), delimiter=',', quotechar='"')

# skip csv header
next(dates_reader, None)

for row in dates_reader:
    url = row[0]
    begin_date = row[1]
    end_date = row[2]

    anidb.update(
        {'url': url}, 
        {'$set': {
            'begin_date': begin_date, 
            'end_date': end_date 
            },
         '$unset': {
            'Year' : ""
            }
        })
