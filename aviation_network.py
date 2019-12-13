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
import math
import pprint
import numpy as np
import pandas as pd
import networkx as nx
from keplergl import KeplerGl
from num2words import num2words


# +
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
        '''
        Map nodes and edges to a directed graph.
        '''
        for airport in self.airport_df.itertuples():
            node_in = airport.iata + '_in'
            node_out = airport.iata + '_out'
            self.DG.add_edge('Source', node_in, capacity=float('inf'))
            self.DG.add_edge(node_in, node_out, capacity=airport.init_capacity)
            self.DG.add_edge(node_out, 'Target', capacity=float('inf'))
    
    def _get_airport_info(self):
        '''
        Get all the airports info from the given airport_df
        '''
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
        '''
        Compute impact to an airport based on the given current capacity,
        security level, and number of attacks.
        '''
        if num_attacks == 3:
            return 0
        K = 5.0 - security_level / 10.0
        weight = 0.8 * (-(num_attacks - 3) / 3.0) ** K + 0.2
        return curr_capacity * weight
    
    def _filter_airports(self, v, max_attack_per_airport):
        '''
        '''
        return v['number_of_attacks'] < max_attack_per_airport
    
    def _get_attackable_airports(self, d, max_attack_per_airport):
        '''
        Get a list of attackable airports based on the given maximum number of
        attacks to each airport.
        '''
        return dict((k, v) for (k, v) in d.items() if self._filter_airports(v, max_attack_per_airport))
        
    def print_result(self, seq, airport_iata, airport_info, new_capacity):
        '''
        Print out basic results after an attack.
        '''
        seq = num2words(seq, to='ordinal_num')
        airport_name = airport_info['name']
        num_attacks = airport_info['number_of_attacks']
        init_cap = airport_info['init_capacity']
        sec_level = airport_info['security_level']
        print(f'{seq} attack: {airport_name} ({airport_iata})')
        print(f'The initial capacity: {init_cap}')
        print(f'The capacity after the attack: {new_capacity:.2f}')
        print(f'Security level: {sec_level}')
        print(f'Total number of attacks to this airport: {num_attacks}')
        print('--------------------------------------------------')
    
    def _compute_max_flow(self, DG):
        '''
        Compute a total maximum flow of the given directed graph.
        '''
        total_max_flow = 0
        for (_, _, c) in DG.edges.data('capacity'):
            if not math.isinf(c):
                total_max_flow += c
        return total_max_flow
    
    def _compute_percentage_diff(self, prev, curr):
        '''
        Compute a percentage difference between the given two values.
        '''
        return (prev - curr) / ((prev + curr) / 2) * 100
    
    def _compute_points_diff(self, prev, curr):
        '''
        '''
        return -(prev - curr)
    
    def print_curr_max_flow(self, seq, airport_iata,
                            curr_percent_diff, pts_diff, total_max_flow):
        '''
        Print out a current maximum flow of the given directed graph.
        '''
        seq = num2words(seq, to='ordinal_num')
        print(f'{seq} & {airport_iata} & {total_max_flow:,.0f} & {curr_percent_diff:.2f}\% & {pts_diff:.2f}pts \\\ ')
    
    def compute_min_max_flow(self, max_attacks=15, max_attack_per_airport=1):
        '''
        Compute minimum maximum flow for every attack until the given maximum
        number of attacks.
        '''
        airport_info = self._get_airport_info()
        copied_DG = self.DG.copy()
        prev_total_max_flow = self._compute_max_flow(copied_DG)
        prev_percent_diff = 0
        for seq in range(1, max_attacks + 1):
            attackable_airports = self._get_attackable_airports(airport_info, max_attack_per_airport)
            temp_airports = list()
            temp_flow_vals = list()
            temp_new_caps = list()
            for (node, airport) in attackable_airports.items():
                temp_DG = copied_DG.copy()

                node_in = airport['node_in']
                node_out = airport['node_out']

                curr_capacity = temp_DG[node_in][node_out]['capacity']
                new_capacity = self._compute_attack_impact(
                    curr_capacity,
                    airport['security_level'],
                    airport['number_of_attacks'] + 1)
                new_node = [(
                    node_in,
                    node_out,
                    { 'capacity': new_capacity }
                )]
                temp_DG.update(new_node)

                flow_value = nx.maximum_flow_value(temp_DG, 'Source', 'Target')
                temp_airports.append(node)
                temp_flow_vals.append(flow_value)
                temp_new_caps.append(new_capacity)
                del temp_DG

            idx = np.argmin(temp_flow_vals)
            airport_iata = temp_airports[idx]
            curr_airport_data = airport_info[airport_iata]
            curr_airport_data['sequence'] = seq
            curr_airport_data['flow_value'] = temp_flow_vals[idx]
            curr_airport_data['number_of_attacks'] = curr_airport_data['number_of_attacks'] + 1
            airport_info.update({ airport_iata: curr_airport_data })

            new_capacity = [(
                airport_iata + '_in',
                airport_iata + '_out',
                { 'capacity': temp_new_caps[idx] }
            )]
            copied_DG.update(new_capacity)
            
#             total_max_flow = self._compute_max_flow(copied_DG)
            curr_total_max_flow = self._compute_max_flow(copied_DG)
            curr_percent_diff = self._compute_percentage_diff(prev_total_max_flow, curr_total_max_flow)
            pts_diff = self._compute_points_diff(prev_percent_diff, curr_percent_diff)
            self.print_curr_max_flow(seq, airport_iata,
                                     curr_percent_diff, pts_diff, curr_total_max_flow)
            
            prev_percent_diff = curr_percent_diff
            prev_total_max_flow = curr_total_max_flow
            
#             curr_percentage_diff = self._compute_percentage_diff(curr_total_max_flow, total_max_flow)

        del copied_DG
        return airport_info
