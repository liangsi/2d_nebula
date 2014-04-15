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
            anime['type'] = res['obj'].get('type', 'N/A')
            anime['begin_date'] = res['obj']['begin_date']
            anime['end_date'] = res['obj']['end_date']
            anime['directors'] = res['obj']['directors']
            anime['company'] = res['obj']['company']
            anime['creator'] = res['obj']['creator']
            anime['desc'] = res['obj']['desc'][0] if res['obj']['desc'] else []

            animes.append(anime)

        return animes

    def get_details(oid):
        # TODO add object id to related
        result = self.integrated.find_one({'_id': ObjectId(oid)})
        return result
