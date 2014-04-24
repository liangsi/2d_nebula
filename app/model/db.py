from pymongo import MongoClient
from bson.objectid import ObjectId


class Database():

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
                db.integrated.ensureIndex({'desc': 'text', 'directors':'text', 'creators':'text', 'title': 'text'})

        full text search on fields: desc, directors, creator, title
        TODO: create a list of casts and characters, create text index on these two filed
        '''
        results = self.db.command(
            'text',
            'integrated',
            search=keywords,
            limit=10)['results']

        animes = []
        for res in results:
            anime = {}
            anime['oid'] = str(res['obj']['_id'])
            anime['title'] = res['obj']['title']
            anime['image_file'] = res['obj']['image_files'][0] if len(res['obj']['image_files']) > 0 else '/static/images/default.jpg'
            anime['released_type'] = res['obj'].get('released_type', 'unknown')
            anime['released_episodes'] = res['obj'].get('released_episodes', 'unknown')
            anime['begin_date'] = res['obj']['begin_date']
            anime['end_date'] = res['obj']['end_date']
            anime['directors'] = res['obj']['directors']
            anime['company'] = res['obj']['company']
            anime['creators'] = res['obj']['creators']
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
                related_anime = self.integrated.find_one({'absoluteanime_url' : res['url']})

                if not related_anime:
                    continue

                anime = {}
                anime['oid'] = str(related_anime['_id'])
                anime['title'] = related_anime['title']
                anime['image_file'] = related_anime['image_files'][0] if len(related_anime['image_files']) > 0 else '/static/images/default.jpg'

                related_animes.append(anime)

        # pick one image to display
        result['image_file'] = result['image_files'][0] if len(result['image_files']) > 0 else '/static/images/default.jpg'
        # pick one desc
        result['desc'] = sorted(result['desc'], key=len)[-1] if result['desc'] else []

        return result, related_animes
