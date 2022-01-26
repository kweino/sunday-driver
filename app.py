import streamlit as st
import os
import pandas as pd
from dotenv import dotenv_values
from opencage.geocoder import OpenCageGeocode
import geopandas
from shapely.geometry import Point
import altair as alt
from vega_datasets import data

from road_recommender import create_model, get_recommendations
from helper import get_route_coords, make_route_map, get_data

##### Data & Variable Definition #####
config = dotenv_values(".env")

#df = pd.read_csv('data/MR_Route_Data.csv')
df = get_data('data/route_df.pkl')
route_gdf = get_data('data/route_gdf.pkl')
route_marks_df = get_data('data/route_marks_df.pkl')

##### START OF PAGE #####


st.title('Sunday Driver: A Motorcycle Road Recommendation Engine')
st.markdown('''
    **Sunday Driver** provides recommendations for roads near a user's location
    that are highly rated by motorcyclists. Just put an address in the
    form below to find some new routes!
''')

# User form
with st.form(key='my_form'):
     user_address = st.text_input('Address')
     num_routes_desired = st.slider('How many suggested routes would you like?',1,10)
     show_state_routes = st.checkbox("Show a map of all the routes in your state")
     submit_button = st.form_submit_button('Get Routes!')

if submit_button:
    key = config['GEOCODE-API-KEY']
    geocoder = OpenCageGeocode(key)
    results = geocoder.geocode(user_address)

    if results:
        user_loc = Point(results[0]['geometry']['lng'],results[0]['geometry']['lat'] )
        user_state = results[0]['components']['state']

        #fit model for number of user routes
        features, model = create_model(num_routes_desired)

        # find MR road closest to user Location
        closest_gpx =  (
            route_gdf
            [route_gdf.rep_point.distance(user_loc) == route_gdf.rep_point.distance(user_loc).min()]
            .iloc[0].gpx_file_num
        )

        closest_index = df[df.gpx_file_num == closest_gpx].index[0]

        # recommend routes from engine based on road MR found above
        recommended_roads = get_recommendations(features, model, closest_index)

        # map those roads
        for gpx in recommended_roads.gpx_file_num:
            rec_route = df[df.gpx_file_num == gpx]
            st.subheader(rec_route.name.values[0])
            st.map(get_route_coords(gpx))

            col1, col2, col3 = st.columns(3)
            col1.markdown('**Scenery:**')
            col1.write(f'{rec_route.scenery_description.values[0]}')
            col2.markdown('**Drive Enjoyment:**')
            col2.write(f'{rec_route.drive_enjoyment_description.values[0]}')
            col3.markdown('**Tourism:**')
            col3.write(f'{rec_route.tourism_description.values[0]}')

        if show_state_routes:
            st.subheader(f'Explore all the best motorcycle routes in {user_state}:')
            MR_route_map = make_route_map(route_gdf,user_state)
            st.plotly_chart(MR_route_map, use_container_width = True)

    else:
        st.write('**Unexpected error!** Try your query again.')


st.header('The story behind Sunday Driver')

with st.form(key='routes_form'):
    st.write('Click this button to generate an interactive map of all the routes in this database')
    sub_button = st.form_submit_button('See All Routes!')

if sub_button:
    with st.spinner('Generating map...'):
        MR_route_map = make_route_map(route_marks_df)
        st.plotly_chart(MR_route_map, use_container_width = True)

st.balloons()
