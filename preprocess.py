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

# + colab={"base_uri": "https://localhost:8080/", "height": 122} colab_type="code" executionInfo={"elapsed": 30741, "status": "ok", "timestamp": 1574653712743, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="NJCINpMz5-LL" outputId="a3228c62-8952-44a2-bbad-3a23f78101b5"
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from keplergl import KeplerGl
from collections import defaultdict

# + [markdown] colab_type="text" id="GEOG4uus5-LN"
# ## 1. Get airport info

# + colab={} colab_type="code" id="B4M1gTCr5-LO"
airport_cols = ['type', 'name', 'iso_country', 'iso_region', 'iata_code', 'coordinates']
airport_df = pd.read_csv('./raw_data/airport-codes.csv', header=0, usecols=airport_cols)

airport_col_names = ['facility_type', 'name', 'country', 'region', 'iata', 'coordinates']
airport_df.columns = airport_col_names

# + colab={"base_uri": "https://localhost:8080/", "height": 0} colab_type="code" executionInfo={"elapsed": 32923, "status": "ok", "timestamp": 1574653714933, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="OrPOjsvm5-LQ" outputId="7f29a871-ef4d-4b2d-bfe4-d102fa6bca9e"
filter_airports = ['small_airport', 'medium_airport', 'large_airport']
airport_df = airport_df[airport_df.country == 'US']
airport_df = airport_df[airport_df.facility_type.isin(filter_airports)]

coordinates = np.array([tuple(crd.split(',')) for crd in airport_df.coordinates.tolist()])
airport_df['latitude'] = list(map(float, coordinates[:, 0]))
airport_df['longitude'] = list(map(float, coordinates[:, 1]))
airport_df.drop(labels='coordinates', axis='columns', inplace=True)

airport_df.dropna(axis='index', subset=['iata'], inplace=True)
airport_df.reset_index(drop=True, inplace=True)
airport_df

# + colab={"base_uri": "https://localhost:8080/", "height": 0} colab_type="code" executionInfo={"elapsed": 32918, "status": "ok", "timestamp": 1574653714933, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="APOoXNf75-LT" outputId="dbb1fcc1-b527-482f-df8b-e43e5617b812"
airport_df[airport_df.iata == 'JFK']

# + colab={"base_uri": "https://localhost:8080/", "height": 0} colab_type="code" executionInfo={"elapsed": 32915, "status": "ok", "timestamp": 1574653714934, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="tS9Pv_2K5-LV" outputId="35d38b54-d0b7-4ec0-8e82-56b8bb1df5a0"
airport_map = KeplerGl(height=900, width=800)
airport_map_data = airport_df[['name', 'latitude', 'longitude', 'facility_type']]
airport_map.add_data(data=airport_map_data[airport_map_data.facility_type == 'large_airport'], name='large_airports')
airport_map.add_data(data=airport_map_data[airport_map_data.facility_type == 'medium_airport'], name='medium_airports')
airport_map.add_data(data=airport_map_data[airport_map_data.facility_type == 'small_airport'], name='small_airports')
airport_map.save_to_html(file_name='./visualization/airport_map.html')
# airport_map

# + [markdown] colab_type="text" id="uJf8Ce225-LY"
# ## 2. Get flight info

# + colab={"base_uri": "https://localhost:8080/", "height": 0} colab_type="code" executionInfo={"elapsed": 39951, "status": "ok", "timestamp": 1574653721974, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="IN6ZY7qS5-LY" outputId="9b70a9cf-0857-4370-f401-d81fc28e2bbb"
flight_df = pd.read_csv('./raw_data/266694930_T_ONTIME_REPORTING.csv', header=0)
flight_df.columns = [col.lower() for col in flight_df.columns.tolist()]

# + colab={"base_uri": "https://localhost:8080/", "height": 0} colab_type="code" executionInfo={"elapsed": 41216, "status": "ok", "timestamp": 1574653723243, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="y-u1C4OX5-La" outputId="88c5f28a-777f-4998-8550-92ff5234d177"
flight_df

# + colab={} colab_type="code" id="lW8_yzoW5-Lc"
flights = flight_df[['origin', 'dest']].to_records(index=False).tolist()     
unique_flights = defaultdict(int)
for key, flight in enumerate(flights):
    unique_flights[flight] += 1

# + colab={"base_uri": "https://localhost:8080/", "height": 0} colab_type="code" executionInfo={"elapsed": 41803, "status": "ok", "timestamp": 1574653723839, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="uDQYJxsh5-Ld" outputId="1b8ff0c1-78ab-4afe-a77f-41c39d1ef68d"
unique_flights_list = list()
for route, num in unique_flights.items():
    unique_flights_list.append((route[0], route[1], num))
unique_flights_list[:10]

# + [markdown] colab_type="text" id="2RjwVUqUEQK9"
# ## 3. Export data

# + [markdown] colab_type="text" id="mD-UWTVUIKTj"
# ### Export edges.csv

# + colab={} colab_type="code" id="EopqeHrO5-Lf"
edges_df_columns = ['origin', 'dest', 'num_of_flights']
edges_df = pd.DataFrame(unique_flights_list, columns=edges_df_columns)
edges_df.to_csv('./processed_data/edges.csv', index=False)

# + colab={"base_uri": "https://localhost:8080/", "height": 419} colab_type="code" executionInfo={"elapsed": 42477, "status": "ok", "timestamp": 1574653724518, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="_-c4WTRD5-Lg" outputId="744efa96-39e3-41f8-b675-72a4592d4467"
edges_df

# + [markdown] colab_type="text" id="sXGF2X2_INiq"
# ### Export vertices.csv

# + colab={} colab_type="code" id="o5tHXFScGaFY"
inflow_dict = defaultdict(int)
outflow_dict = defaultdict(int)
for (origin, dest, num) in edges_df.itertuples(index=False):
    inflow_dict[dest] += num
    outflow_dict[origin] += num
outflow_dict

def _get_init_capacity(row):
    curr_airport = row['iata']
    return outflow_dict[curr_airport] + inflow_dict[curr_airport]
airport_df['init_capacity'] = airport_df.apply(_get_init_capacity, axis=1)


# + colab={} colab_type="code" id="ADpwZmHCGaXS"
def _encode_security_level(row):
    facility_type = row['facility_type']
    if facility_type == 'small_airport':
        return 10
    elif facility_type == 'medium_airport':
        return 20
    elif facility_type == 'large_airport':
        return 30
    else:
        raise
airport_df['security_level'] = airport_df.apply(_encode_security_level, axis=1)


# +
def _get_in_charge(row):
    return True if row['latitude'] < 40 and -130 < row['longitude'] < -85 else False

airport_df['in_charge'] = airport_df.apply(_get_in_charge, axis=1)

# + colab={"base_uri": "https://localhost:8080/", "height": 297} colab_type="code" executionInfo={"elapsed": 42469, "status": "ok", "timestamp": 1574653724520, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="mq4dO-ugNNiU" outputId="4dc1acb1-150f-4329-c34d-46ff15baad09"
airport_df.describe()

# + colab={} colab_type="code" id="pZR_-GQQ-tZ7"
airport_df = airport_df[['iata', 'name', 'country', 'region', 'latitude', 'longitude', 'facility_type', 'init_capacity', 'security_level', 'in_charge']]
airport_df.to_csv('./processed_data/vertices.csv', index=False)

# + colab={"base_uri": "https://localhost:8080/", "height": 419} colab_type="code" executionInfo={"elapsed": 43745, "status": "ok", "timestamp": 1574653725803, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="RaM_eT0JEoAT" outputId="c330d397-8fbb-493c-9fe0-610ef89236af"
airport_df

# + colab={"base_uri": "https://localhost:8080/", "height": 80} colab_type="code" executionInfo={"elapsed": 453, "status": "ok", "timestamp": 1574653728955, "user": {"displayName": "So Negishi", "photoUrl": "", "userId": "14957100293746809516"}, "user_tz": 300} id="xfXpih_hrNz-" outputId="8bf3df1f-8411-43f1-ef2f-a789b57cb46d"
airport_df[airport_df.iata == 'IND']

# + colab={} colab_type="code" id="ZNlLEWBsrRaz"
airport_df[airport_df.in_charge == True].describe()
# -

airport_df.describe()
