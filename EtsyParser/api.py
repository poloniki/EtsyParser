import logging
import os
import aiohttp
import streamlit as st

api = os.environ.get("ETSYAPI")
api = st.secrets["ETSYAPI"] #"https://openapi.etsy.com/v3/application/"



async def get(uri, arguments=None):
    url = f'{base_url}{uri}'
    arg = {'client_id': api}
    if arguments:
        arg.update(arguments)

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=arg) as response:
            #logging.info(f'Version 1 API RUN {url}{arguments}')
            return await response.json(content_type=None)


# V2 API
base_url_v2 = "https://openapi.etsy.com/v2/"


async def getv2(uri, arguments=None):

    url = f'{base_url_v2}{uri}'
    arg = {'api_key': api}
    if arguments:
        arg.update(arguments)

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=arg) as response:
            #logging.info(f'Version 2 API RUN  {url}{arguments}')
            return await response.json(content_type=None)
