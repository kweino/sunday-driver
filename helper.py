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

def get_plotting_zoom_level_and_center_coordinates_from_lonlat_tuples(longitudes=None, latitudes=None):
    """Function documentation:\n
    Basic framework adopted from Krichardson under the following thread:
    https://community.plotly.com/t/dynamic-zoom-for-mapbox/32658/7

    # NOTE:
    # THIS IS A TEMPORARY SOLUTION UNTIL THE DASH TEAM IMPLEMENTS DYNAMIC ZOOM
    # in their plotly-functions associated with mapbox, such as go.Densitymapbox() etc.

    Returns the appropriate zoom-level for these plotly-mapbox-graphics along with
    the center coordinate tuple of all provided coordinate tuples.
    """

    # Check whether both latitudes and longitudes have been passed,
    # or if the list lenghts don't match
    if ((latitudes is None or longitudes is None)
            or (len(latitudes) != len(longitudes))):
        # Otherwise, return the default values of 0 zoom and the coordinate origin as center point
        return 0, (0, 0)

    # Get the boundary-box
    b_box = {}
    b_box['height'] = latitudes.max()-latitudes.min()
    b_box['width'] = longitudes.max()-longitudes.min()
    b_box['center']= (np.mean(longitudes), np.mean(latitudes))

    # get the area of the bounding box in order to calculate a zoom-level
    area = b_box['height'] * b_box['width']

    # * 1D-linear interpolation with numpy:
    # - Pass the area as the only x-value and not as a list, in order to return a scalar as well
    # - The x-points "xp" should be in parts in comparable order of magnitude of the given area
    # - The zpom-levels are adapted to the areas, i.e. start with the smallest area possible of 0
    # which leads to the highest possible zoom value 20, and so forth decreasing with increasing areas
    # as these variables are antiproportional
    # zoom = np.interp(x=area,
    #                  xp=[0, 5**-10, 4**-10, 3**-10, 2**-10, 1**-10, 1**-5],
    #                  fp=[20, 15,    14,     13,     12,     7,      5])
    # zoom = np.interp(x=area,
    #                  xp=[0.00025, 0.0005, 0.001, 0.003, 0.005, 0.011, 0.022, 0.044, 0.088, 0.176, 0.352, 0.703, 1.406,
    #                      2.813, 5.625,11.25, 22.5, 45],
    #                  fp=[20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3])
    # Finally, return the zoom level and the associated boundary-box center coordinates
    return zoom, b_box['center']
