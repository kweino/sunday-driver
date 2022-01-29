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
import streamlit as st

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
    '''takes a gpx_file_num and returns a dataframe of the lat/lon points'''
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
