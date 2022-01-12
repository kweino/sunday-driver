from gpx_converter import Converter
import pandas as pd
import numpy as np
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from os.path import exists as file_exists
#gpx_file = 'deal-s-gap--aka--the-dragon--or--tail-of-the-dragon--.gpx'

def calcluate_sinuosity(gpx_file_num):
    gpx_file = 'gpx_files/' + str(gpx_file_num) + '.gpx'
    if file_exists(gpx_file):
        gpx_array = Converter(input_file=gpx_file).gpx_to_numpy_array()
        start_pt = gpx_array[0]
        end_pt = gpx_array[-1]
        route = LineString(gpx_array)
        route_SL = LineString((start_pt, end_pt))
        route_sinuosity = route.length / route_SL.length
        return route_sinuosity
    else:
        return 0


def sinuosity_classifier(sinuosity):
    if sinuosity < 1.05:
        return f'This road is almost straight. Sinuosity = {sinuosity}'
    if 1.05 <= sinuosity < 1.25 :
        return f'This road is winding. Sinuosity = {sinuosity}'
    if 1.25 <= sinuosity < 1.5:
        return f'This road is twisty. Sinuosity = {sinuosity}'
    else:
        return f'This road is meandering. Sinuosity = {sinuosity}'

# sinuosity = calcluate_sinuosity(gpx_array)
# print(sinuosity_classifier(sinuosity))

