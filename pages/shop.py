import streamlit as st
import aiohttp
import asyncio


from EtsyParser.shop_analytics import basic_shop_info,get_shop_id,stat_of_shop_listings


shop = st.text_input('Shop name',value="DoodleLettersStore")

if "load_state" not in st.session_state:
     st.session_state.load_state = False



async def main():
    button = st.button('Search')
    if button or st.session_state.load_state:
        st.session_state.load_state=True
        shop_id = await get_shop_id(shop)
        response = await basic_shop_info(shop_id)
        st.dataframe(response)
        top10button = st.button('Get Top10 items')
        if top10button:
            print('Im here')
            top_10 = await stat_of_shop_listings(shop_id)
            top_10 = top_10.to_html(escape=False)
            st.write(top_10, unsafe_allow_html=True)


# make each button press toggle that entry in the session state.






if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
