# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
__author__ = 'So Negishi'
__copyright__ = 'Copyright 2019, So Negishi'
__license__ = 'GPL'
__version__ = '0.0.1'
__maintainer__ = 'So Negishi'
__email__ = 'sonegishi_2020@depauw.edu'
__status__ = 'Development'

# %%
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from keplergl import KeplerGl


# %%
class AviationMap:
    def __init__(self, airport_df, flight_df):
        self.airport_df = airport_df
        self.flight_df = flight_df
        self.airport_dict = None
        self.airport_list = None
        self.flight_list = None
        
        self._create_airport_dict()
        self._create_airport_list()
        self._create_flight_list()
    
    def _create_airport_dict(self):
        airport_dict = dict()
        for airport in self.airport_df.itertuples():
            airport_dict[airport.iata] = {
                'name': airport.name,
                'country': airport.country,
                'region': airport.region,
                'latitude': airport.latitude,
                'longitude': airport.longitude,
                'facility_type': airport.facility_type,
                'init_capacity': airport.init_capacity,
                'security_level': airport.security_level
            }
        self.airport_dict = airport_dict
    
    def _create_airport_list(self):
        airport_list = list()
        for airport in self.airport_df.itertuples():
            airport_list.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point', 'coordinates': [airport.longitude, airport.latitude]
                },
                'properties': {
                    'name': airport.name,
                    'country': airport.country,
                    'region': airport.region,
                    'latitude': airport.latitude,
                    'longitude': airport.longitude,
                    'facility_type': airport.facility_type,
                    'init_capacity': airport.init_capacity,
                    'security_level': airport.security_level
                }
            })
        self.airport_list = airport_list
    
    def _create_flight_list(self):
        flight_list = list()
        for flight in self.flight_df.itertuples():
            origin = flight.origin
            dest = flight.dest
            flight_list.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString', 'coordinates': [
                        (self.airport_dict[origin]['longitude'], self.airport_dict[origin]['latitude']),
                        (self.airport_dict[dest]['longitude'], self.airport_dict[dest]['latitude'])
                    ]
                },
                'properties': {
                    'origin_country': self.airport_dict[origin]['country'],
                    'origin_airport': self.airport_dict[origin]['name'],
                    'origin_longitude': self.airport_dict[origin]['longitude'],
                    'origin_latitude': self.airport_dict[origin]['latitude'],
                    'dest_country': self.airport_dict[dest]['country'],
                    'dest_airport': self.airport_dict[dest]['name'],
                    'dest_longitude': self.airport_dict[dest]['longitude'],
                    'dest_latitude': self.airport_dict[dest]['latitude']
                }
            })
        self.flight_list = flight_list
    
    def create_map(self, filename='airport_map'):
        flight_map = KeplerGl(height=500, width=800)

        flight_feature_collection = {
            'type': 'FeatureCollection',
            'features': self.flight_list
        }

        large_airport_feature_collection = {
            'type': 'FeatureCollection',
            'features': [airport for airport in self.airport_list if airport['properties']['facility_type'] == 'large_airport']
        }

        medium_airport_feature_collection = {
            'type': 'FeatureCollection',
            'features': [airport for airport in self.airport_list if airport['properties']['facility_type'] == 'medium_airport']
        }

        small_airport_feature_collection = {
            'type': 'FeatureCollection',
            'features': [airport for airport in self.airport_list if airport['properties']['facility_type'] == 'small_airport']
        }

        flight_map.add_data(data=flight_feature_collection, name='flights')
        flight_map.add_data(data=large_airport_feature_collection, name='large_airports')
        flight_map.add_data(data=medium_airport_feature_collection, name='medium_airports')
        flight_map.add_data(data=small_airport_feature_collection, name='small_airports')

        flight_map.save_to_html(file_name=f'{filename}.html')
        return flight_map
