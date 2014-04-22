import csv
import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from nltk.metrics import edit_distance

def union(name_list1, name_list2):
    names = []

    for name1 in sorted(name_list1):
        for name2 in sorted(name_list2):
            #name1_bigram = set(bigrams(name1))
            #name2_bigram = set(bigrams(name2))

            distance = edit_distance(name1, name2)

            print name1, name2, distance

            if distance < 5:
                name_list2.pop(0)
                break

        names.append(name1)

    names.extend(name_list2)

    return names

# connect to db
client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime_0418
anidb = db.anidb
integrated = db.integrated_0418

# open the csv exported from FRIL
matches_reader = csv.reader(
    open('result_0418_all.csv', 'rU'), delimiter=',', quotechar='"')

# skip csv header
next(matches_reader, None)

for row in matches_reader:
    anidb_id = row[0]
    absoluteanime_id = row[2]

    anidb_obj = anidb.find_one({'_id': ObjectId(anidb_id)})
    absoluteanime_obj = absoluteanime.find_one({'_id': ObjectId(absoluteanime_id)})

    integrated_obj = {}
    # integrated_obj['urls'] = [anidb_url, absoluteanime_url]
    integrated_obj['anidb_url'] = anidb_obj['url']
    integrated_obj['absoluteanime_url'] = absoluteanime_obj['url']

    integrated_obj['images'] = []
    integrated_obj['images'].extend([anidb_obj.get('image')] if anidb_obj.get('image', None) else [])
    integrated_obj['images'].extend([absoluteanime_obj.get('image')] if absoluteanime_obj.get('image', None) else [])
    
    # use longer title
    absolute_title = absoluteanime_obj['jp_info'].get('title', [''])[0]
    if not absolute_title:
        absolute_title = absoluteanime_obj['us_info'].get('title', [''])[0]

    integrated_obj['title'] = anidb_obj['Main_Title'] \
                                if len(anidb_obj['Main_Title']) > len(absolute_title) \
                                else absolute_title

    # user Year in anidb as it is more precise
    # integrated_obj['date'] = anidb_obj['Year']
    integrated_obj['begin_date'] = anidb_obj['begin_date']
    integrated_obj['end_date'] = anidb_obj['end_date']

    # union of companies & animation work
    anidb_obj_animation_work = set(anidb_obj.get('staffs', set()).get('Animation Work', set()))
    absoluteanime_obj_company = set(absoluteanime_obj['jp_info'].get('company', set()))

    integrated_obj['company'] = list(anidb_obj_animation_work.union(absoluteanime_obj_company))

    # use type in anidb, ignore 'released' in absoluteanime
    integrated_obj['released_type'] = anidb_obj.get('released_type', None)
    integrated_obj['released_episodes'] = anidb_obj.get('released_episodes', None)

    # union of genre & Categories
    anidb_obj_categories = set(anidb_obj.get('Categories', set()))
    absoluteanime_obj_genre = set(absoluteanime_obj['jp_info'].get('genre', set()))

    integrated_obj['categories'] = list(anidb_obj_categories.union(absoluteanime_obj_genre))

    # union of creator & original work
    # e.g.: oda eiichirou vs eiichiro oda
    anidb_obj_original_work = anidb_obj.get('staffs', []).get('Original Work', [])
    absoluteanime_obj_creator = absoluteanime_obj['jp_info'].get('creator', [])

    integrated_obj['creators'] = union(anidb_obj_original_work, absoluteanime_obj_creator)

    # union of director & Direction
    # e.g.: oda eiichirou vs eiichiro oda
    anidb_obj_direction = anidb_obj.get('staffs', []).get('Direction', [])
    absoluteanime_obj_director = absoluteanime_obj['jp_info'].get('director', [])

    integrated_obj['directors'] = union(anidb_obj_direction, absoluteanime_obj_director)

    # all description from both data source
    integrated_obj['desc'] = []
    integrated_obj['desc'].extend([anidb_obj.get('desc')] if anidb_obj.get('desc', None) else [])
    integrated_obj['desc'].extend(absoluteanime_obj.get('description', []))

    # all related anime from absoluteanime
    integrated_obj['related'] = absoluteanime_obj['jp_info'].get('related', None)

    # all characters from absoluteanime
    # TODO: integrate with casts in anidb
    
    absoluteanime_obj_chars = absoluteanime_obj['jp_info'].get('characters', [])
    integrated_obj['characters'] = absoluteanime_obj_chars

    # all casts from anidb
    integrated_obj['casts'] = anidb_obj.get('casts', None)

    # average from anidb
    # WTF?
    integrated_obj['average'] = anidb_obj.get('Average', None)

    # rating from anidb
    # TODO: if N/A, replace by None
    integrated_obj['rating'] = anidb_obj.get('Rating', None)

    integrated.insert(integrated_obj)
    # print json.dumps(integrated_obj, sort_keys=True, indent=4)