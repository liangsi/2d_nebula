import simplejson as json
import lxml

from amazonproduct import API


class ObjectJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, lxml.objectify.IntElement):
            return int(o)
        if isinstance(o, lxml.objectify.NumberElement) or isinstance(o, lxml.objectify.FloatElement):
            return float(o)
        if isinstance(o, lxml.objectify.ObjectifiedDataElement):
            return str(o.text.encode('utf-8'))
        if hasattr(o, '__dict__'):
            # For objects with a __dict__, return the encoding of the __dict__
            return o.__dict__
        return json.JSONEncoder.default(self, o)


class AmazonDvd():

    def __init__(self):
        self.api = API(locale='us')

    def find_product(self, keywords, Director=None):
        '''
        return top 3 products
        '''
        try:
            items = self.api.item_search(
                'DVD', Keywords=keywords, Director=None, limit=3,
                Sort='relevancerank', MerchantId='Amazon', ResponseGroup='Large')
        except Exception, e:
            return []
        

        dvds = []
        for item in items:
            json_obj = json.loads(ObjectJSONEncoder().encode(item))

            dvd = {}
            dvd['ASIN'] = json_obj['ASIN']
            dvd['Title'] = json_obj['ItemAttributes']['Title']
            dvd['DetailPageURL'] = json_obj['DetailPageURL']

            if json_obj.get('SmallImage', None):
                dvd['SmallImage'] = json_obj['SmallImage']['URL']

            if json_obj.get('CustomerReviews', None):
                dvd['CustomerReviews'] = json_obj['CustomerReviews']['IFrameURL']

            if json_obj.get('EditorialReviews', None):
                dvd['EditorialReviews'] = json_obj[
                    'EditorialReviews']['EditorialReview']['Content']

            if json_obj.get('OfferSummary', None):
                dvd['LowestNewPrice'] = json_obj['OfferSummary'][
                    'LowestNewPrice']['FormattedPrice']

            if json_obj['ItemAttributes'].get('Actor', None):
                dvd['Actor'] = json_obj['ItemAttributes']['Actor']

            if json_obj['ItemAttributes'].get('Director', None):
                dvd['Director'] = json_obj['ItemAttributes']['Director']

            dvds.append(dvd)
            
        return dvds
