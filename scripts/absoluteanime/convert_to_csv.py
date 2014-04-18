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
absoluteanime = db.absoluteanime

# absoluteanime_csv = codecs.open('absoluteanime.csv', 'w', 'utf-8')
absoluteanime_csv = open('absoluteanime.csv', 'w')

csv_writer = UnicodeWriter(
    absoluteanime_csv, delimiter=",", lineterminator='\n',
    quotechar="\"", quoting=csv.QUOTE_MINIMAL)

csv_writer.writerow(['url', 'main_title', 'official_title', 'date', 'creator',
                    'director', 'genre', 'company', 'released', 'characters', 'description'])

for one in absoluteanime.find():
    url = one['url']
    main_title = one['jp_info'].get('title', [''])[0]
    official_title = one['us_info'].get('title', [''])[0]
    date = one['jp_info'].get('dates', [''])[0]
    creator = ', '.join(one['jp_info'].get('creator', []))
    director = ', '.join(one['jp_info'].get('director', []))
    genre = ', '.join(one['jp_info'].get('genre', []))
    company = ', '.join(one['jp_info'].get('company', []))
    released = one['jp_info'].get('released', [''])[0]
    description = one.get('description', [''])[0]

    characters = []

    jp_chars = []
    for jp_char in one['jp_info'].get('characters', []):
        if jp_char['name'] != '--?--':
            jp_chars.append(jp_char['name'])

    if len(jp_chars) == 0:
        us_chars = []
        for us_char in one['us_info'].get('characters', []):
            if us_char['name'] != '--?--':
                us_chars.append(us_char['name'])
        characters = ', '.join(us_chars)

    else:
        characters = ', '.join(jp_chars)

    csv_writer.writerow(
        [url, main_title, official_title, date, creator, director, genre, company, released, characters, description])

absoluteanime_csv.close()
