# Helper functions
import gzip
import os
import dill
import pandas as pd
import numpy as np
from gpx_converter import Converter
from os.path import exists as file_exists
import plotly.express as px
import geopandas as gpd
import shapely.geometry

def calcluate_sinuosity(gpx_file_num):
    '''calculates the sinuosity of each route from its gpx file of lat/lon coordinates'''
    gpx_file = f'gpx_files/{str(gpx_file_num)}.gpx'
    if file_exists(gpx_file):
        try:
            gpx_array = Converter(input_file=gpx_file).gpx_to_numpy_array()
        except Exception:
            return -1

        splits = 4
        subsets = np.array_split(gpx_array, splits)
        subset_sinuosities = []

        for subset in subsets:
            start_pt = subset[0]
            end_pt = subset[-1]
            route = LineString(subset)
            route_SL = LineString((start_pt, end_pt))
            route_sinuosity = route.length / route_SL.length
            subset_sinuosities.append(route_sinuosity)
        return sum(subset_sinuosities)/splits
    else:
        return -2

def calc_row_sum(cols):
    return pd.DataFrame(cols.apply(lambda x: x.sum(), axis=1))


def get_route_coords(gpx_file_num):
    gpx_file = f'gpx_files/{str(gpx_file_num)}.gpx'
    if file_exists(gpx_file):
        try:
            gpx_df = Converter(input_file=gpx_file).gpx_to_dataframe()
            return gpx_df
        except Exception:
            return None

def get_data(data_path):
    """Return loaded data from disk."""
    with gzip.open(data_path, 'rb') as f:
        return dill.load(f)

def make_route_map(df,state=None):
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
                     mapbox_style="open-street-map", zoom=2)
    return fig
