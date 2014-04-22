import json
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

client = MongoClient('localhost', 27017)
db = client.anime
anidb = db.anidb

# absoluteanime_csv = codecs.open('absoluteanime.csv', 'w', 'utf-8')
anidb_csv = open('anidb_0418.csv', 'w')

csv_writer = UnicodeWriter(
    anidb_csv, delimiter=",", lineterminator='\n',
    quotechar="\"", quoting=csv.QUOTE_MINIMAL)

csv_writer.writerow(['oid', 'main_title', 'creator',
                    'director', 'released_type', 'released_episodes'])

for one in anidb.find():
    oid = str(one['_id'])
    main_title = one['Main_Title']

    creator = ', '.join(sorted(one.get('staffs', []).get('Original Work', [])))
    director = ', '.join(sorted(one.get('staffs', []).get('Direction', [])))

    released_type = str(one['released_type']) if one['released_type'] else ""
    released_episodes = str(one['released_episodes']) if one['released_episodes'] else ""

    csv_writer.writerow(
        [oid, main_title, creator, director, released_type, released_episodes])

anidb_csv.close()
