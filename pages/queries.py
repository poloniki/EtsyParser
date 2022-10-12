import streamlit as st
import aiohttp
import asyncio
import pandas as pd

from EtsyParser.find_listings import find_listing_info
from EtsyParser.hash_analytics import get_trending


query = st.text_input('Query',value="Casa de papel")

if "load_state" not in st.session_state:
     st.session_state.load_state = False



async def main():
    button = st.button('Search')
    if button or st.session_state.load_state:
        st.session_state.load_state=True
        response, top_10_hash = await find_listing_info(query)
        response = response.to_html(escape=False)
        st.write(response, unsafe_allow_html=True)
        st.text(f'Tags: {top_10_hash}')
        competition = st.button('Check hashtags competition')
        if competition:

            comp = await get_trending(top_10_hash)
            df =pd.DataFrame(comp).T
            df.columns = ['Competition', 'Query number', 'Score']
            st.write(df, unsafe_allow_html=True)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
