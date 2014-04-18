import csv
import codecs
import cStringIO

from pymongo import MongoClient


class UnicodeWriter:

    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

absolute_dates_csv = open('absolute_dates.csv', 'w')
csv_writer = UnicodeWriter(
    absolute_dates_csv, delimiter=",", lineterminator='\n',
    quotechar="\"", quoting=csv.QUOTE_MINIMAL)

client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime
anidb = db.anidb

for anime in absoluteanime.find():
    url = anime['url']
    dates = anime['jp_info'].get('dates', None)

    if dates:
        for date in dates:
            csv_writer.writerow([url, date])

absolute_dates_csv.close()

anidb_dates_csv = open('anidb_dates.csv', 'w')
csv_writer = UnicodeWriter(
    anidb_dates_csv, delimiter=",", lineterminator='\n',
    quotechar="\"", quoting=csv.QUOTE_MINIMAL)

for anime in anidb.find():
    url = anime['url']
    date = anime['Year']

    csv_writer.writerow([url, date])

anidb_dates_csv.close()