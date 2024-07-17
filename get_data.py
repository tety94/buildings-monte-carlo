import geopandas as gpd
import pandas as pd
from mysql.connector import (connection)

CRS_PIEMONTE = 32632
CRS_PIEMONTE_STRING = 'EPSG:32632'
CRS_MARCATORE_STRING = 'EPSG:4326'
CRS_MARCATORE = 4326

def get_data(TORINO=True):
    cnx = connection.MySQLConnection(user='###', password='###',
                                     host='127.0.0.1',
                                     database='###', auth_plugin='mysql_native_password')

    # prendo i condomini doppi, eccetera
    cursor = cnx.cursor()
    query = (
        "select id, lat, lng, city, parals_codals, n_after_removing_mutation, n_after_removing_mutation_and_familial, arpa_building_id from historicals  where to_use = 1 and n_after_removing_mutation_and_familial > 0")
    cursor.execute(query)
    registro_dtf = pd.DataFrame(cursor.fetchall(),
                                columns=['id', 'lat', 'lng', 'city', 'codals_parals', 'n_after_removing_mutation',
                                         'n_after_removing_mutation_and_familial', 'arpa_id_edificio'])

    registro_gdf = gpd.GeoDataFrame(registro_dtf, geometry=gpd.points_from_xy(registro_dtf.lng, registro_dtf.lat),
                                    crs=CRS_MARCATORE_STRING)
    registro_gdf.set_crs(epsg=4326, inplace=True, allow_override=True)
    registro_gdf.to_crs(epsg=CRS_PIEMONTE, inplace=True)

    if TORINO:
        condomini_risultanti = registro_gdf[registro_gdf['city'].str.lower() == 'torino']
    else:
        condomini_risultanti = registro_gdf[registro_gdf['city'].str.lower() != 'torino']

    cursor = cnx.cursor()
    query = (
        "select id, lat, lng, city, parals_codals, n_after_removing_mutation, n_after_removing_mutation_and_familial, arpa_building_id from historicals  where to_use = 1")
    cursor.execute(query)
    storico_totale = pd.DataFrame(cursor.fetchall(),
                                  columns=['id', 'lat', 'lng', 'city', 'codals_parals', 'n_after_removing_mutation',
                                           'n_after_removing_mutation_and_familial', 'arpa_building_id'])

    if TORINO:
        storico_totale = storico_totale[storico_totale['city'].str.lower() == 'torino']
    else:
        storico_totale = storico_totale[storico_totale['city'].str.lower() != 'torino']

    storico_totale_gdf = gpd.GeoDataFrame(storico_totale,
                                          geometry=gpd.points_from_xy(storico_totale.lng, storico_totale.lat),
                                          crs=CRS_MARCATORE_STRING)
    storico_totale_gdf.set_crs(epsg=4326, inplace=True, allow_override=True)
    storico_totale_gdf.to_crs(epsg=CRS_PIEMONTE, inplace=True)

    # muted
    cursor = cnx.cursor()
    query = ("select parals_codals from registro_mutaz where mutaz not in ('', 'WT')")
    cursor.execute(query)
    mutaz = [x[0] for x in cursor.fetchall()]

    # familial
    cursor = cnx.cursor()
    query = ("select parals_codals from registro_famil where famalial = 'S' ")
    cursor.execute(query)
    familial = [x[0] for x in cursor.fetchall()]

    storico_totale_gdf = storico_totale_gdf[~storico_totale_gdf['codals_parals'].isin(mutaz)]
    storico_totale_gdf = storico_totale_gdf[~storico_totale_gdf['codals_parals'].isin(familial)]

    return condomini_risultanti, storico_totale_gdf


def count_lines(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            file.close()
            return len(lines)
    except FileNotFoundError:
        return 0


def add_line(filename, line, count_lines):
    if count_lines < 10002:
        with open(filename, 'a') as file:
            file.write(line + '\n')
            file.close()
