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
integrated = db.integrated_0420


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
            simi = jellyfish.levenshtein_distance(
                anidb_name, name.encode('utf-8'))

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


def trainDT():
    f = open('training_set.csv', 'r')
    data_set = []
    tag_set = []

    for line in f.readlines(100):
        train = line.split(',')[4:11]
        tag = line.split(',')[11].strip()

        data_set.append(train)
        tag_set.append(tag)

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(data_set, tag_set)

    return clf

def union_names(anidb_names, absolute_names):
    if not anidb_names and not absolute_names:
        return []
    
    if not anidb_names:
        return absolute_names

    if not absolute_names:
        return anidb_names

    anidb_names_copy = list(anidb_names)
    absolute_names_copy = list(absolute_names)
    name_matches = {}

    while anidb_names_copy:
        anidb_name = anidb_names_copy.pop()

        for name in absolute_names_copy:
            simi = jellyfish.levenshtein_distance(
                anidb_name, name.encode('utf-8'))

            if simi < 5:
                absolute_names_copy.pop(0)
                name_matches[anidb_name] = name
                break

    total_distinct_names = anidb_names
    total_distinct_names.extend([name for name in absolute_names if name not in name_matches.values()])

    return total_distinct_names

def integrate(anidb_obj, absolute_obj):
    integrated_obj = {}
    # integrated_obj['urls'] = [anidb_url, absoluteanime_url]
    integrated_obj['anidb_url'] = anidb_obj['url']
    integrated_obj['absoluteanime_url'] = absolute_obj['url']

    integrated_obj['images'] = []
    integrated_obj['images'].extend([anidb_obj.get('image')] if anidb_obj.get('image', None) else [])
    integrated_obj['images'].extend([absolute_obj.get('image')] if absolute_obj.get('image', None) else [])
    
    # use anidb Main_Title
    # absolute_title = absolute_obj['jp_info'].get('title', [''])[0]
    # if not absolute_title:
    #     absolute_title = absolute_obj['us_info'].get('title', [''])[0]
    integrated_obj['title'] = anidb_obj['Main_Title']

    # user begin_date and end_date in anidb as it is more precise
    # integrated_obj['date'] = anidb_obj['Year']
    integrated_obj['begin_date'] = anidb_obj['begin_date']
    integrated_obj['end_date'] = anidb_obj['end_date']

    # union of companies & animation work
    anidb_obj_animation_work = set(anidb_obj.get('staffs', set()).get('Animation Work', set()))
    absolute_obj_company = set(absolute_obj['jp_info'].get('company', set()))

    integrated_obj['company'] = list(anidb_obj_animation_work.union(absolute_obj_company))

    # use released_type and released_episodes in anidb
    integrated_obj['released_type'] = anidb_obj.get('released_type', None)
    integrated_obj['released_episodes'] = anidb_obj.get('released_episodes', None)

    # union of genre & Categories
    anidb_obj_categories = set(anidb_obj.get('Categories', set()))
    absolute_obj_genre = set(absolute_obj['jp_info'].get('genre', set()))

    integrated_obj['categories'] = list(anidb_obj_categories.union(absolute_obj_genre))

    # union of creator & original work
    # e.g.: oda eiichirou vs eiichiro oda
    anidb_obj_original_work = anidb_obj.get('staffs', []).get('Original Work', [])
    absolute_obj_creator = absolute_obj['jp_info'].get('creator', [])

    integrated_obj['creators'] = union_names(anidb_obj_original_work, absolute_obj_creator)

    # union of director & Direction
    # e.g.: oda eiichirou vs eiichiro oda
    anidb_obj_direction = anidb_obj.get('staffs', []).get('Direction', [])
    absolute_obj_director = absolute_obj['jp_info'].get('director', [])

    integrated_obj['directors'] = union_names(anidb_obj_direction, absolute_obj_director)

    # all description from both data source
    integrated_obj['desc'] = []
    integrated_obj['desc'].extend([anidb_obj.get('desc')] if anidb_obj.get('desc', None) else [])
    integrated_obj['desc'].extend(absolute_obj.get('description', []))

    # all related anime from absoluteanime
    integrated_obj['related'] = absolute_obj['jp_info'].get('related', None)

    # union characters from anidb and absoluteanime
    anidb_obj_chars = []
    for cast in anidb_obj_casts:
        anidb_obj_chars.append(reverse_words(cast['char']))

    absolute_obj_chars = []
    absolute_obj_characters = absolute_obj['jp_info'].get('characters', [])

    for char in absolute_obj_characters:
        absolute_obj_chars.append(char['name'])

    integrated_obj['characters'] = union_names(anidb_obj_chars, absolute_obj_chars)

    # all casts from anidb
    integrated_obj['casts'] = anidb_obj.get('casts', None)

    # average from anidb
    integrated_obj['average'] = anidb_obj.get('Average', None)

    # rating from anidb
    integrated_obj['rating'] = anidb_obj.get('Rating', None)

    integrated.insert(integrated_obj)


# train DT model
clf = trainDT()

count = 0
# for each possible match, compute a simi vector
# use decision tree to determine if the match is correct or not
# if the match is correct, then integrate them
# else check next pair
for anidb_obj in anidb.find():
    # enable ful text search: 
    #    db.adminCommand({setParameter:true, textSearchEnabled:true})
    results = db.command(
        'text',
        'absoluteanime_0418',
        search=anidb_obj['Main_Title'],
        limit=10)['results']

    possible_matches = {}

    for absolute_obj in results:

        # compute title similarities between a title from
        # anidb and a list of titles from absoluteanime
        # if one of the title pairs has similarity > 0.9, keep going
        # other wise, skip this matching
        absolute_titles = list(absolute_obj['obj']['us_info'].get('title', []))
        absolute_titles.extend(absolute_obj['obj']['jp_info'].get('title', []))
        title_simi = match_title(anidb_obj['Main_Title'], absolute_titles)

        if title_simi:
            # title similarity higher than 0.9
            # compute similarities of other fields

            # check release type
            anidb_obj_type = anidb_obj['released_type']
            absolute_obj_type = absolute_obj['obj']['jp_info']['released_type']
            type_simi = match_type(anidb_obj_type, absolute_obj_type)

            # check number of release eps
            anidb_obj_eps = anidb_obj['released_episodes']
            absolute_obj_eps = absolute_obj['obj']['jp_info']['released_episodes']
            eps_simi = match_eps(anidb_obj_eps, absolute_obj_eps)

            # check creators
            anidb_obj_creators = anidb_obj.get('staffs', []).get('Original Work', [])
            absolute_obj_creators = absolute_obj['obj']['jp_info'].get('creator', [])
            creators_simi = match_names(anidb_obj_creators, absolute_obj_creators)

            # check directors
            anidb_obj_directors = anidb_obj.get('staffs', []).get('Direction', [])
            absolute_obj_directors = absolute_obj['obj']['jp_info'].get('director', [])
            directors_simi = match_names(anidb_obj_directors, absolute_obj_directors)

            # check characters
            anidb_obj_chars = []
            anidb_obj_casts = anidb_obj.get('casts', [])

            for cast in anidb_obj_casts:
                anidb_obj_chars.append(reverse_words(cast['char']))

            absolute_obj_chars = []
            absolute_obj_characters = absolute_obj['obj']['jp_info'].get('characters', [])

            for char in absolute_obj_characters:
                absolute_obj_chars.append(char['name'])

            chars_simi = match_names(anidb_obj_chars, absolute_obj_chars)

            # check date
            anidb_obj_dates = [(anidb_obj['begin_date'], anidb_obj['end_date'])]
            absolute_obj_dates_list = absolute_obj['obj']['jp_info'].get('dates_refined', [])

            absolute_obj_dates = []
            for date in absolute_obj_dates_list:
                absolute_obj_dates.append((date['begin_date'], date['end_date']))

            date_simi = match_dates(anidb_obj_dates, absolute_obj_dates)

            is_match = int(clf.predict([title_simi, type_simi, eps_simi, creators_simi, directors_simi, chars_simi, date_simi])[0])

            if is_match:
                count += 1
                integrate(anidb_obj, absolute_obj['obj'])
            else:
                pass

print count