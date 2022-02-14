# Helper functions
import gzip
import os
import dill
import pandas as pd
import numpy as np
from gpx_converter import Converter
from os.path import exists as file_exists
import plotly.express as px
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


def get_data(data_path):
    """Return loaded data from disk."""
    with gzip.open(data_path, 'rb') as f:
        return dill.load(f)

def write_data(data, data_path):
    '''Write data to disk'''
    with gzip.open(data_path, 'wb') as f:
        dill.dump(data, f)

def categorize_roads(route_sin):
    if route_sin < 1.25:
        return 'Mostly Straight / Gentle Curves'
    elif 1.25 < route_sin < 1.5:
        return 'Some twists and turns'
    else:
        return 'Twisty!'
