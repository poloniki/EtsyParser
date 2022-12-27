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

import datetime

async def basic_shop_info(shop_id: str) -> pd.DataFrame:
    # fetch the basic shop information
    uri = await basic_shop(shop_id)
    # get the response from the URI
    response = await get(uri)

    # convert the update and creation timestamps to datetime objects
    update_timestamp = int(response['update_date'])
    update_date = datetime.utcfromtimestamp(update_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    creation_timestamp = int(response['create_date'])
    creation_date = datetime.utcfromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    # extract the active listings, sold items, review count, and review average from the response
    active_listings = response['listing_active_count']
    sold_items = response['transaction_sold_count']
    review_count = response['review_count']
    review_average = round(response['review_average'], 2)

    # calculate the average number of sold items per active listing
    items_per_listing = int(round(sold_items/active_listings, 0))

    # create a dataframe with the extracted information
    answer = pd.DataFrame([{'Creation date': creation_date,
                            'Date of last listing': update_date,
                            'Active listings': active_listings,
                            'Sold items': sold_items,
                            'Items per listing': items_per_listing,
                            'Reviews': review_count,
                            'Average review': review_average}]).T
    answer.columns = ['values']

    return answer


async def stat_of_shop_listings(shop_id: str, full_shop: bool = False) -> pd.DataFrame:
    # fetch the active shop listings
    uri = await active_shop_listing(shop_id)

    # get all listings for the shop
    if full_shop:
        # get the total number of listings
        response = await getv2(uri, {'limit': 1})
        count = response['count']
        # calculate the number of pages needed to fetch all listings
        pages = math.ceil(count / 100)
        # get all listings in pages of 100
        all_listings = [await getv2(uri, {'limit':100, 'page': page}) for page in range(1, pages+1)]
    else:
        # get the first page of listings
        all_listings = [await getv2(uri, {'limit': 100, 'page': 1})]

    # extract the results from each page of listings
    all_responses = [listing['results'] for listing in all_listings]
    # flatten the list of results
    all_responses = [item for sublist in all_responses for item in sublist]
    # create a dictionary mapping titles to views
    all_title_views = {response['title']: response['views'] for response in all_responses}
    # count the occurrences of each title
    counter = Counter(all_title_views)
    # get the top 10 most viewed listings
    top_10 = counter.most_common(10)
    # extract the titles and views from the top 10 listings
    titles = [item[0] for item in top_10]
    views = [item[1] for item in top_10]
    # create a dictionary mapping titles to URLs
    all_title_views = {response['title']: response['url'] for response in all_responses if response['title'] in titles}

    # create a dataframe with the title and view count for the top 10 listings
    df = pd.DataFrame({'Title': titles, 'Purchases': views})

    def make_clickable(title):
        # make the title a clickable link to the listing's URL
        return '<a target="_blank" href="{}">{}</a>'.format(all_title_views[title], title)

    df['Title'] = df['Title'].apply(make_clickable)

    return df



async def get_shop_id(shop_name):
    shop_id = await getv2('shops', {'shop_name': shop_name})
    shop_id = shop_id['results'][0]['shop_id']
    return shop_id
