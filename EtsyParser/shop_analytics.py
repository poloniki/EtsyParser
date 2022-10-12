from datetime import datetime
import pandas as pd
ts = int("1284101485")
from EtsyParser.api import get, getv2
import math
from collections import Counter



async def active_shop_listing(shop_id):
    uri = f'shops/{shop_id}/listings/active'
    return uri

async def basic_shop(shop_id):
    uri = f'shops/{shop_id}'
    return uri

async def basic_shop_info(shop_id):

    uri = await basic_shop(shop_id)
    response = await get(uri)
    date = datetime.utcfromtimestamp(int(response['update_date'])).strftime('%Y-%m-%d %H:%M:%S')
    creation_date = datetime.utcfromtimestamp(int(response['create_date'])).strftime('%Y-%m-%d %H:%M:%S')
    active_listings = response['listing_active_count']
    sold_items = response['transaction_sold_count']
    review_count = response['review_count']
    review_average = round(response['review_average'],2)

    answer = pd.DataFrame([{'Creation date':creation_date,
                           'Date of las listing':date,
                           'Active listings':active_listings,
                           'Sold items':sold_items,
                           'Items p/listing':int(round(sold_items/active_listings,0)),
                           'Reviews':review_count,
                           'AVG review':review_average}]).T
    answer.columns = ['values']
    return answer


async def stat_of_shop_listings(shop_id, full_shop=False):

    uri = await active_shop_listing(shop_id)

    if full_shop:
        response = await getv2(uri, {'limit': 1})
        pages = math.ceil(response['count'] / 100)
        all_listings = [await getv2(uri, {'limit':100, 'page': each}) for each in range(1,pages+1)]
    else:
        all_listings = [await getv2(uri, {'limit': 100, 'page': each}) for each in range(1, 2)]

    all_responses = [listing['results'] for listing in all_listings]
    all_responses = [every for each in all_responses for every in each]
    all_title_views = {each['title']:each['views'] for each in all_responses}
    k = Counter(all_title_views)

    top_10 = k.most_common(10)
    titles = [each[0] for each in top_10]
    views = [each[1] for each in top_10]
    all_title_views = {each['title']: each['url'] for each in all_responses if each['title'] in titles}

    df = pd.DataFrame({'Title':titles, 'Purchases':views})

    def make_clickable(title):
        return '<a target="_blank" href="{}">{}</a>'.format(all_title_views[title], title)
    df['Title'] = df['Title'].apply(make_clickable)


    return df


async def get_shop_id(shop_name):
    shop_id = await getv2('shops', {'shop_name': shop_name})
    shop_id = shop_id['results'][0]['shop_id']
    return shop_id
