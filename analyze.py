# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

__author__ = 'So Negishi'
__copyright__ = 'Copyright 2019, So Negishi'
__license__ = 'GPL'
__version__ = '0.0.2'
__maintainer__ = 'So Negishi'
__email__ = 'sonegishi_2020@depauw.edu'
__status__ = 'Development'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pandas as pd
from keplergl import KeplerGl
from collections import defaultdict, OrderedDict
from aviation_map import AviationMap
from aviation_network import AviationNetwork

# ## Import data

vertices_df = pd.read_csv('./processed_data/vertices.csv', header=0)
print(vertices_df.shape)
vertices_df = vertices_df[
    (vertices_df.in_charge) &
    (vertices_df.name.str.contains('Air Force Base') == False) &
    (vertices_df.init_capacity != 0)]
print(vertices_df.shape)
vertices_df.tail(5)

edges_df = pd.read_csv('./processed_data/edges.csv', header=0)
print(edges_df.shape)
unique_airport_list = vertices_df.iata.unique()
edges_df = edges_df[(edges_df.origin.isin(unique_airport_list)) & (edges_df.dest.isin(unique_airport_list))]
print(edges_df.shape)
edges_df.tail(5)

# ## Export a map

aviation_map = AviationMap(vertices_df, edges_df)
aviation_map.create_map(filename='./visualization/ns_flight_map')

# ## Solve the maximum flow problem

aviation_network = AviationNetwork(vertices_df)
results = aviation_network.compute_min_max_flow(max_attacks=15, max_attack_per_airport=1)
