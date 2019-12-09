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
__version__ = '0.0.1'
__maintainer__ = 'So Negishi'
__email__ = 'sonegishi_2020@depauw.edu'
__status__ = 'Development'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import pprint
import numpy as np
import pandas as pd
import networkx as nx
from keplergl import KeplerGl


class AviationNetwork:
    def __init__(self, airport_df):
        self.airport_df = airport_df
        self.airport_dict = None
        self.airport_list = None
        self.flight_list = None
        
        self.DG = nx.DiGraph()
        self.pp = pprint.PrettyPrinter(indent=2, compact=True)
        
        self._create_airport_dict()
        
    def _create_airport_dict(self):
        # Set vertices
        for airport in self.airport_df.itertuples():
            node_in = airport.iata + '_in'
            node_out = airport.iata + '_out'
            self.DG.add_edge('Source', node_in, capacity=float('inf'))
            self.DG.add_edge(node_in, node_out, capacity=airport.init_capacity)
            self.DG.add_edge(node_out, 'Target', capacity=float('inf'))
    
    def _get_airport_info(self):
        airport_info = dict()
        for airport in self.airport_df.itertuples():
            airport_info[airport.iata] = {
                'name': airport.name,
                'country': airport.country,
                'region': airport.region,
                'latitude': airport.latitude,
                'longitude': airport.longitude,
                'facility_type': airport.facility_type,
                'init_capacity': airport.init_capacity,
                'security_level': airport.security_level,
                'node_in': airport.iata + '_in',
                'node_out': airport.iata + '_out',
                'number_of_attacks': 0,
                'sequence': None,
                'flow_value': None
        }
        return airport_info
        
    def _compute_attack_impact(self, curr_capacity, security_level, num_attacks):
        """
        """
        K = 1.0 / 3.0 * math.log(0.2, security_level)
        return curr_capacity * (1.0 - math.pow(security_level, -(K * num_attacks)))
    
    def _filter_airports(self, v, max_attack_per_airport):
        return v['number_of_attacks'] < max_attack_per_airport
    
    def _get_attackable_airports(self, d, max_attack_per_airport):
        return dict((k, v) for (k, v) in d.items() if self._filter_airports(v, max_attack_per_airport))
    
    def compute_min_max_flow(self, max_attacks=15, max_attack_per_airport=1):
        """
        """
        airport_info = self._get_airport_info()
        copied_DG = self.DG.copy()
        for seq in range(1, max_attacks + 1):
            attackable_airports = self._get_attackable_airports(airport_info, max_attack_per_airport)
            temp_airports = list()
            temp_flow_vals = list()
            for (node, airport) in attackable_airports.items():
                temp_DG = copied_DG.copy()

                node_in = airport['node_in']
                node_out = airport['node_out']

                curr_capacity = temp_DG[node_in][node_out]['capacity']
                new_capacity = [(
                    node_in,
                    node_out,
                    {
                        'capacity': self._compute_attack_impact(
                            curr_capacity,
                            airport['security_level'],
                            airport['number_of_attacks'])
                    }
                )]
                temp_DG.update(new_capacity)

                flow_value = nx.maximum_flow_value(temp_DG, 'Source', 'Target')
                temp_airports.append(node)
                temp_flow_vals.append(flow_value)
                del temp_DG

            idx = np.argmin(temp_flow_vals)
            airport_iata = temp_airports[idx]
            curr_airport_data = airport_info[airport_iata]
            curr_airport_data['sequence'] = seq
            curr_airport_data['flow_value'] = temp_flow_vals[idx]
            curr_airport_data['number_of_attacks'] = curr_airport_data['number_of_attacks'] + 1

            airport_info.update({ airport_iata: curr_airport_data })
            self.pp.pprint(airport_info[airport_iata])

            new_capacity = [(
                airport_iata + '_in',
                airport_iata + '_out',
                { 'capacity': temp_flow_vals[idx] }
            )]
            copied_DG.update(new_capacity)

        del copied_DG
        return airport_info
