import collections
import math
from EtsyParser.api import getv2
import datetime
from datetime import datetime
from collections import Counter
import logging
import pandas as pd
today = datetime.now()


async def find_listing_info(query):
    uri = 'listings/active'

    response = await getv2(uri, {'keywords': query, 'limit': 1})
    pages = math.ceil(response['count'] / 100)
    logging.info(f'{response["count"] }')

    if pages > 10:
        pages = 10
    logging.info(f'Страниц {pages}')
    all_listings = [await getv2(uri, {'keywords': query, 'limit': 100}) for each in range(0, pages)]
    all_responses = [listing['results'] for listing in all_listings]
    all_responses = [every for each in all_responses for every in each]
    # Add new field - number of views per day

    count = 1
    for each in all_responses:
        hours = max(int(round((today - datetime.utcfromtimestamp(int(each['creation_tsz']))).seconds / 60 / 60, 2)),1)
        views_per_day = int(round(each['views'] / hours, 0))
        each.update({'views_per_day': views_per_day})
        each.update({'hours_since': hours})

    all_title_views = {each['title']: each['views_per_day'] for each in all_responses}

    k = Counter(all_title_views)
    top_10 = k.most_common(10)
    titles = [each[0] for each in top_10]
    top_50 = k.most_common(50)
    titles_for_hash = [each[0] for each in top_50]

    # Получаем самые выделяющиеся слова
    # Для начала получаем список всех тегов
    try:
        all_tags = []
        for each in all_responses:
            all_tags.extend(each['tags'])
        # Теперь считаем вхождение каждого отдельного ключа
        occurrences = collections.Counter(all_tags)
        # Теперь для каждого тайтла определяем какое слово - какой имеет вес
        hash_dict = {each['title']:each['tags'] for each in all_responses if each['title'] in titles}
        for each in hash_dict.keys():

            list_to_process = hash_dict[each]

            new_dict = {}
            for every in list_to_process:
                if occurrences[every] > 0:
                    result = 1 / occurrences[every]
                else:
                    result = 0
                dict_result = {every:result}
                new_dict.update(dict_result)
            hash_dict.update({each: new_dict})
        #logging.info(f'{hash_dict}')
    except Exception as err:
        logging.info(f'{err}')

    all_title_views = {each['title']: each['url'] for each in all_responses if each['title'] in titles}
    all_title_views2 = {}
    for each in all_responses:
        if each['title'] in titles:
            all_title_views2.update({each['title']: each['hours_since']})

    # What are best hashtags for this top
    best_hashes = []
    for each in all_responses:
        if each['title'] in titles_for_hash:
            best_hashes.extend(each['tags'])



    occurrences = collections.Counter(best_hashes)
    hash = Counter(occurrences)
    top_10_hash = hash.most_common(10)
    top_10_hash = [each[0] for each in top_10_hash]

    queries = [each[0] for each in top_10]
    views = [each[1] for each in top_10]
    #breakpoint()
    df = pd.DataFrame({'Query':queries, 'Views per day':views})
    def make_clickable(title):
        return '<a target="_blank" href="{}">{}</a>'.format(all_title_views[title], title)
    def get_hours(title):
        return all_title_views2[title]
    #df['Hours'] = df['Query'].apply(get_hours)

    df['Query'] = df['Query'].apply(make_clickable)


    return df, top_10_hash

    # return "\n".join([
    #     f"{num + 1}. <i><a href='{all_title_views[user[0]]}'>{user[0]}</a></i>:  <b>{user[1]:,}</b> просмотров в час за последние {all_title_views2[user[0]]} ч.\n"
    #     for num, user in enumerate(top_10)
    # ]), top_10_hash
