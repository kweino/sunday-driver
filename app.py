import streamlit as st
import os
import pandas as pd
from dotenv import dotenv_values
from opencage.geocoder import OpenCageGeocode
import geopandas
from shapely.geometry import Point
import plotly.express as px

from road_recommender import create_model, get_recommendations
from helper import get_route_coords, get_data

##### Data, Variables, Configurations #####
config = dotenv_values(".env")
geocode_key = config['GEOCODE-API-KEY']

df = get_data('data/route_df.pkl')
route_gdf = get_data('data/route_gdf.pkl')
route_marks_long = get_data('data/route_marks_long.pkl')

st.set_page_config(layout="wide")

##### Functions #####
def display_route_info(rec_route,gpx):

    st.subheader(rec_route.name.values[0])

    # route metrics
    route_len = round(rec_route.route_length.values[0])
    route_sin = round(rec_route.sinuosity.values[0],2)
    user_rate = rec_route.user_rating.values[0]

    len_dif = route_len - df.route_length.median()
    sin_dif = ((route_sin - df.sinuosity.median()) / abs(df.sinuosity.median())) *100
    rate_dif = ((user_rate - df.user_rating.median()) / abs(df.user_rating.median())) *100


    met1, met2, met3 = st.columns(3)
    met1.metric('Length',
                f'{route_len} miles',
                f'{round(len_dif,1)} miles')
    met2.metric('Sinuosity',
                route_sin,
                f'{round(sin_dif,2)}%')
    met3.metric('MR.com User Rating',
                user_rate,
                f'{round(rate_dif,1)}%')
    st.write('(Route metrics compared to database median values)')

    # route map
    fig = px.line_mapbox(get_route_coords(gpx), lat="latitude", lon="longitude",
                         mapbox_style='open-street-map',height=500)
    fig.update_geos(fitbounds="locations")

    st.plotly_chart(fig, use_container_width=True)

    # st.markdown(f'Need Directions? Download the [GPX file](https://www.motorcycleroads.com/downloadgpx/{gpx}).')

    col1, col2, col3 = st.columns(3)

    with col1.expander('Scenery'):
        st.write(f'{rec_route.scenery_description.values[0]}')
    with col2.expander('Drive Enjoyment'):
        st.write(f'{rec_route.drive_enjoyment_description.values[0]}')
    with col3.expander('Tourism'):
        st.write(f'{rec_route.tourism_description.values[0]}')
    st.markdown('---')

def make_big_map(df,state=None):
    if state:
        geo_df = df[df.state == state].reset_index(drop=True)

        lats = []
        lons = []
        names = []
        states = []

        for feature, name, state in zip(geo_df.geometry, geo_df.route_name, geo_df.state):
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [name]*len(y))
                states = np.append(states, [state]*len(y))
                lats = np.append(lats, None)
                lons = np.append(lons, None)
                names = np.append(names, None)
                states = np.append(states, None)

        fig = px.line_mapbox(lat=lats, lon=lons, hover_name=names,
                             mapbox_style="open-street-map", zoom=4)
    else:
        #For mapping all the routes in the database
        geo_df = df
        fig = px.line_mapbox(geo_df, lat='lat', lon='lon', hover_name='name',
                     mapbox_style="open-street-map", height=600, zoom=4)

    # fig.update_geos(fitbounds="locations")
    return fig

##### SIDEBAR FEATURES #####
with st.sidebar.form(key='route_rec_form'):
    user_address = st.text_input('Enter an address:')
    num_routes_desired = st.slider('How many suggested routes would you like?',1,10)
    show_state_routes = st.checkbox("Show a map of all the routes in your state")
    route_rec_button = st.form_submit_button('Get Routes!')

with st.sidebar.form(key='all_routes_form'):
    st.write('Generate an interactive map of all the routes in this database')
    all_routes_button = st.form_submit_button('See All Routes!')

with st.sidebar.form(key='data_story_form'):
    st.write('Learn the story behind Sunday Driver')
    data_story_button = st.form_submit_button('Tell me more!')

##### ROUTE RECOMMENDER #####
if route_rec_button:
    geocoder = OpenCageGeocode(geocode_key)
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
            display_route_info(rec_route,gpx)

        # map all the routes in a given state
        if show_state_routes:
            st.subheader(f'Explore all the best motorcycle routes in {user_state}:')
            MR_route_map = make_big_map(route_gdf,user_state)
            st.plotly_chart(MR_route_map, use_container_width = True)

    else:
        st.write('**Unexpected error!** Try your query again.')


##### MAP TO ALL ROUTES #####
elif all_routes_button:
    with st.spinner('Generating map...'):
        MR_route_map = make_big_map(route_marks_long)
        st.plotly_chart(MR_route_map, use_container_width = True)

##### DATA STORY PAGE #####
elif data_story_button:
    st.title('The story of Sunday Driver')
    col1, col2 = st.columns(2)
    col1.markdown('''
        As an avid motorcyclist, I've always been frustrated by Google Maps any
        time I want to plan a ride. The 'driving' mode prioritizes efficiency at the cost
        of quality experience along the journey, presenting me with routes along main throughfares and
        busy interstates and promising very little in the way of ride enjoyment.
        The 'bicycling' mode chooses some roads that may be better for motorcycles,
        but it also allows dirt roads that my street tires just can't handle.

        So for this capstone project, I set out to create an app that would show me great
        roads to ride on my motorcycle, no matter where I was in the US. Think of it
        as the 'motorcyle' travel mode button for Google Maps. But what exactly makes
        a road 'great' for motorcyclists? This capstone project centers around that question.

        To bring this question into the realm of data science, I searched the web
        for websites that might lend answers and found [MotorcycleRoads.com](https://www.motorcycleroads.com).
        The site is a social network of motorcyclists. Users can find, rate, and
        make comments on roads already on the site, post new roads they've ridden
        that aren't already on the site, and  they can even find information about
        motorcycle clubs and places to hang out. Bill Belei, the site's founder,
        [started the site because he too was challenged](https://www.motorcycleroads.com/about-us)
        by the task of finding a great place to ride a motorcyle.
    ''')
    col2.image('data/bike_rect.jpeg') #Me on the motorcycle

    st.markdown(f'''
        ---
        As you can see in the short video below, MR.com was a treasure trove of information
        about each route. I built three Scrapy spiders to scrape basic route details
        and descriptions, route ranking stats, comments users made, and attched GPX files
        (XML files full of route lat/lon tuples) for each of the {len(df)} routes currently on MR.com.
    ''')
    video_file = open('videos/MRcom_page.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

    st.markdown('''
        My first model attempted to learn something about the website features by
        trying to predict the user rating for each route, based
        on a variety of features I scraped from MR.com

        I think the poor performance of the model is mostly due to the clustering
        of user ratings. This makes sense since the routes on the site are user-generated
        by a community avid motorcyclists.

        Topic modeling of the route comments
    ''')
    st.image('data/roadsmap.png') # map of all the roads, colored by user rating

    st.markdown('''
        The recommendation engine ...
    ''')
##### LANDING PAGE #####
else: #not (route_rec_button) or (all_routes_button) or (data_story_button):
    st.title('Sunday Driver: A Motorcycle Road Recommendation Engine')
    st.markdown('''
        **Sunday Driver** provides recommendations for roads near a user's location
        that are highly rated by motorcyclists. Just put an address in the
        form to the left to find some new routes! Check out a sample of the route data below.

        ---
    ''')
    rand_route = df.sample(1)
    #st.write(rand_route)
    display_route_info(rand_route, gpx=rand_route.gpx_file_num.values[0])
