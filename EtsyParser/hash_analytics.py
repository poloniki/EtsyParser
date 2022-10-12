import logging
from datetime import datetime

from EtsyParser.api import getv2
import numpy as np
today = datetime.now()

async def get_trending(list_of_hashtags):
    uri = 'listings/active'
    try:
        hash_dict = {}
        for each in list_of_hashtags:

            response = await getv2(uri, {'keywords': each, 'limit': 100, 'sort_on': 'created', 'sort_order': 'down'})
            # count = response['count']
            recent_count = 1
            one_day_views = 0

            for every in response['results']:

                creation_date = datetime.utcfromtimestamp(int(every['creation_tsz']))
                num_of_hours = int((today- creation_date).seconds / 60 / 60)
                if num_of_hours < 12:
                    recent_count += 1
                    one_day_views += int(every['views'])
                last_25_ratio = recent_count / 100

                views_of_recent = int(round(one_day_views / recent_count,0))

                competition_score = max(int((np.log(last_25_ratio ** 50) * -1 -1) * views_of_recent / 1000),0)

                hash_dict.update({each: [last_25_ratio, views_of_recent, competition_score]})
        print(hash_dict)

        hash_dict = {k: v for k, v in sorted(hash_dict.items(), key=lambda item: item[1][2], reverse=True)}
        return hash_dict


    except Exception as err:
        return logging.info(f'{err}')
