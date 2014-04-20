import math
import re

import jellyfish
from sklearn import tree
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
db = client.anime
absoluteanime = db.absoluteanime_0418
anidb = db.anidb


def match_title(anidb_title, absolute_titles):
    max_simi = 0

    for title in absolute_titles:
        simi = jellyfish.jaro_winkler(anidb_title, title.encode('utf-8'))

        if simi > 0.9 and simi > max_simi:
            max_simi = simi

    if max_simi > 0:
        return max_simi
    else:
        return 0

def match_type(anidb_type, absolute_type):
    # if not the same
    if anidb_type and absolute_type and anidb_type != absolute_type:
        return 0
    elif anidb_type and absolute_type:
        return 1
    else:
        return 0.5

def match_eps(anidb_eps, absolute_eps):

    if anidb_eps and absolute_eps:
        diff = math.fabs(anidb_eps - absolute_eps)
    else:
        return 0.5
    
    if diff < 2:
        return 1
    elif diff > 10:
        return 0
    else:
        return 0.5

def match_names(anidb_names, absolute_names):
    if not anidb_names or not absolute_names:
        return 0.5

    anidb_names_copy = list(anidb_names)
    absolute_names_copy = list(absolute_names)
    name_matches = {}

    while anidb_names_copy:
        anidb_name = anidb_names_copy.pop()

        for name in absolute_names_copy:
            simi = jellyfish.levenshtein_distance(anidb_name, name.encode('utf-8'))
            
            if simi < 5:
                absolute_names_copy.pop(0)
                name_matches[anidb_name] = name
                break

    if len(name_matches):
        return 1
    else:
        return 0
    #shared_names = name_matches.keys()
    #total_distinct_names = anidb_names
    #total_distinct_names.extend([name for name in absolute_names if name not in name_matches.values()])

def match_dates(anidb_dates, absolute_dates):
    if not absolute_obj_dates:
        return 0.5

    if anidb_dates[0][0] == '?':
        return 0.5

    for anidb_date in anidb_dates:
        for absolute_date in absolute_dates:
            anidb_begin_year = re.search('[0-9]{4}', anidb_date[0])
            absolute_begin_year = re.search('[0-9]{4}', absolute_date[0])

            if anidb_begin_year and absolute_begin_year:
                if anidb_begin_year.group() == absolute_begin_year.group():
                    return 1

            anidb_end_year = re.search('[0-9]{4}', anidb_date[1])
            absolute_end_year = re.search('[0-9]{4}', absolute_date[1])

            if anidb_end_year and absolute_end_year:
                if anidb_end_year.group() == absolute_end_year.group():
                    return 1

    return 0

            

def reverse_words(text):
    return ' '.join(text.split(' ')[::-1]) 

# print '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ('anidb_id', 'absolute_id', 'anidb_url', 'absolute_url', 'title', 'type', 'eps', 'creators', 'directors', 'characters', 'date')

f = open('20_percent_for_tagging_100.csv', 'r')
data_set = []
tag_set = []

for line in f.readlines(100):
    train = line.split(',')[4:11]
    tag = line.split(',')[11].strip()

    data_set.append(train)
    tag_set.append(tag)

clf = tree.DecisionTreeClassifier()
clf = clf.fit(data_set, tag_set)

for one in anidb.find():
    title = one['Main_Title']
    oid = one['_id']

    results = db.command(
        'text',
        'absoluteanime_0418',
        search=title,
        limit=10)['results']

    possible_matches = {}

    for obj in results:

        # compute title similarities between a title from
        # anidb and a list of titles from absoluteanime
        # if one of the title pairs has similarity > 0.9, keep going
        # other wise, skip this matching
        absolute_titles = list(obj['obj']['us_info'].get('title', []))
        absolute_titles.extend(obj['obj']['jp_info'].get('title', []))
        title_simi = match_title(title, absolute_titles)

        if title_simi:
            # title similarity higher than 0.9
            # compute similarities of other fields

            # check release type
            anidb_obj_type = one['released_type']
            absolute_obj_type = obj['obj']['jp_info']['released_type']
            type_simi = match_type(anidb_obj_type, absolute_obj_type)

            # check number of release eps
            anidb_obj_eps = one['released_episodes']
            absolute_obj_eps = obj['obj']['jp_info']['released_episodes']
            eps_simi = match_eps(anidb_obj_eps, absolute_obj_eps)

            # check creators
            anidb_obj_creators = one.get('staffs', []).get('Original Work', [])
            absolute_obj_creators = obj['obj']['jp_info'].get('creator', [])
            creators_simi = match_names(anidb_obj_creators, absolute_obj_creators)

            # check directors
            anidb_obj_directors = one.get('staffs', []).get('Direction', [])
            absolute_obj_directors = obj['obj']['jp_info'].get('director', [])
            directors_simi = match_names(anidb_obj_directors, absolute_obj_directors)

            # check characters
            anidb_obj_chars = []
            anidb_obj_casts = one.get('casts', [])

            for cast in anidb_obj_casts:
                anidb_obj_chars.append(reverse_words(cast['char']))

            absolute_obj_chars = []
            absolute_obj_characters = obj['obj']['jp_info'].get('characters', [])

            for char in absolute_obj_characters:
                absolute_obj_chars.append(char['name'])

            chars_simi = match_names(anidb_obj_chars, absolute_obj_chars)

            # check date
            anidb_obj_dates = [(one['begin_date'], one['end_date'])]
            absolute_obj_dates_list = obj['obj']['jp_info'].get('dates_refined', [])

            absolute_obj_dates = []
            for date in absolute_obj_dates_list:
                absolute_obj_dates.append((date['begin_date'], date['end_date']))

            date_simi = match_dates(anidb_obj_dates, absolute_obj_dates)

            is_match = int(clf.predict([title_simi, type_simi, eps_simi, creators_simi, directors_simi, chars_simi, date_simi])[0])

            print '%s,%s,%s,%s,%d' % (str(one['_id']),str(obj['obj']['_id']),one['url'],obj['obj']['url'],is_match)
            # print '%s,%s,%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f' % (str(one['_id']),str(obj['obj']['_id']),one['url'],obj['obj']['url'],title_simi, type_simi, eps_simi, creators_simi, directors_simi, chars_simi, date_simi)

            




