import json

import flickrapi

class Flickr(object):

    def __init__(self):
        self.api_key = 'cc116455ef46bac54656bf51ed3f8665'
        self.secret = '0ba2cf9d9433057f'

        self.api = flickrapi.FlickrAPI(self.api_key, self.secret)

    def get_photos(self, keywords):
        '''
        http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg
            or
        http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}_[mstzb].jpg  <-- use this one
            or
        http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)
        '''
        response = self.api.photos_search(text=keywords, per_page=10)
        photos = []

        for node in response.findall('.//photo'):
            url = 'http://farm%s.staticflickr.com/%s/%s_%s_z.jpg' % (node.get('farm'), node.get('server'), node.get('id'), node.get('secret'))
            photos.append(url)

        return photos
