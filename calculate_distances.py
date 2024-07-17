import pandas as pd
import numpy as np
import geopandas as gpd
from mysql.connector import (connection)
from geopy.distance import geodesic

cnx = connection.MySQLConnection(user='###', password='###', host='127.0.0.1',
                              database='###', auth_plugin='mysql_native_password')

cursor = cnx.cursor()

query = ("select id, lat, lng, codals_parals from storico  where to_use = 1 "
         " and province in ('TO', 'CN', 'AL', 'VB', 'AT', 'NO', 'VC', 'BI', 'AO')"
         )

cursor.execute(query)

registro_dtf = pd.DataFrame(cursor.fetchall(), columns=['id', 'lat', 'lng', 'codals_parals'] )
cursor.close()
print(registro_dtf)

CRS_PIEMONTE = 32632
CRS_MARCATORE = 4326
CRS_PIEMONTE_STRING = 'EPSG:32632'
CRS_MARCATORE_STRING = 'EPSG:4326'

registro_gdf = gpd.GeoDataFrame(registro_dtf, geometry=gpd.points_from_xy(registro_dtf.lng, registro_dtf.lat))
registro_gdf = registro_gdf.set_crs(CRS_MARCATORE_STRING)
registro_gdf = registro_gdf.to_crs(epsg= CRS_MARCATORE)

print(registro_gdf.shape)


def calculate_distance_to_point_of_interest_numpy(point_of_interest,points):
    return np.array([geodesic(point_of_interest, (point.y, point.x)).meters for point in points])


#todo
for index, row in registro_gdf.iterrows():
    print(row['id'])
    if(row['id'] <= '###'): #TODO: number to reply to restart the algorithm
        continue

    if True: #TODO:  reply True/False to restart the algorithm
        cursor = cnx.cursor()
        query = f"select historical_1, historical_2 from historical_distances where " \
                f" historical_1 = %s or historical_2 = %s"
        cursor.execute(query, (row['id'], row['id']))

        historical_instances_already_seen = cursor.fetchall()
        cursor.close()
        historical_instances_already_seen = [list(ele) for ele in historical_instances_already_seen]
        historical_instances_already_seen = [j for sub in historical_instances_already_seen for j in sub]
        historical_instances_already_seen.append(row['id'])
        registro_gdf_for_distances = registro_gdf[~registro_gdf['id'].isin(historical_instances_already_seen)].copy(deep=True)
    else:
        registro_gdf_for_distances = registro_gdf[registro_gdf['id'] > row['id']].copy(deep=True)


    if len(registro_gdf_for_distances) > 0:
        point_of_interest = (row.geometry.y,row.geometry.x)

        registro_gdf_for_distances['distance'] = calculate_distance_to_point_of_interest_numpy(
            point_of_interest,
            registro_gdf_for_distances['geometry'])
        registro_gdf_for_distances = registro_gdf_for_distances[registro_gdf_for_distances['distance'] <= 100]
        registro_gdf_for_distances['historical_1'] = row['id']
        registro_gdf_for_distances['codice_1'] = row['codals_parals']

        query = "INSERT INTO historical_distances (historical_1 , historical_2, distance, codice_1, codice_2) VALUES (%s, %s, %s, %s, %s)"
        cursor = cnx.cursor()

        data = registro_gdf_for_distances[['historical_1', 'id', 'distance', 'codice_1', 'codals_parals']].values.tolist()
        cursor.executemany(query, data)

        # Committing the transaction
        cnx.commit()

        # Closing the cursor and connection
        cursor.close()