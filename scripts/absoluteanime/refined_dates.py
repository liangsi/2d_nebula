import csv

from pymongo import MongoClient

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime

dates_reader = csv.reader(
    open('absolute_dates-0418.csv', 'rU'), delimiter=',', quotechar='"')

# skip csv header
next(dates_reader, None)

for row in dates_reader:
    url = row[0]
    begin_date = row[1]
    end_date = row[2]

    date = {
        'begin_date' : begin_date,
        'end_date' : end_date
    }

    absoluteanime.update(
        {'url': url}, 
        {'$push': {
            'jp_info.dates_refined': date, 
            },
        })
