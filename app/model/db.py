from pymongo import MongoClient
from bson.objectid import ObjectId


class Database(object):

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.anime
        self.integrated = self.db.integrated

    def search(self, keywords):
        '''
        this function requires:
            1. enable text search in mongodb
                db.adminCommand({setParameter:true, textSearchEnabled:true})
            2. create full text index
                db.integrated.ensureIndex({'desc': 'text', 'directors':'text', 'creator':'text', 'title': 'text'})
        
        full text search on fields: desc, directors, creator, title
        TODO: create a list of casts and characters, create text index on these two filed
        '''
        results = self.db.command(
            'text',
            'integrated',
            search=keywords,
            limit=2)['results']

        animes = []
        for res in results:
            anime = {}
            anime['oid'] = str(res['obj']['_id'])
            anime['title'] = res['obj']['title']
            anime['images'] = res['obj']['images']
            anime['type'] = res['obj'].get('type', 'N/A')
            anime['begin_date'] = res['obj']['begin_date']
            anime['end_date'] = res['obj']['end_date']
            anime['directors'] = res['obj']['directors']
            anime['company'] = res['obj']['company']
            anime['creator'] = res['obj']['creator']
            anime['desc'] = sorted(res['obj']['desc'], key=len)[-1] if res['obj']['desc'] else []

            animes.append(anime)

        return animes

    def get_details(self, oid):
        # TODO add object id to related
        result = self.integrated.find_one({'_id': ObjectId(oid)})

        # related animes(oid, title, img)
        related_animes = []
        if result['related']:
            for res in result['related']:
                self.integrated.find_one({'absoluteanime_url' : anime['url']})

                anime = {}
                anime['oid'] = str(res['obj']['_id'])
                anime['title'] = res['title']
                anime['images'] = res['images']

                related_animes.append(anime)

        return result, related_animes
