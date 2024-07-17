import numpy as np
import pandas as pd
from utilities import generate_closest_array
import random
from collections import Counter
from scipy import stats
from get_data import get_data, count_lines, add_line

TORINO = True

prefix = 'Piemonte'
if TORINO:
    prefix = 'Torino'

CRS_PIEMONTE = 32632
CRS_PIEMONTE_STRING = 'EPSG:32632'
CRS_MARCATORE_STRING = 'EPSG:4326'
CRS_MARCATORE = 4326


results_filename = f"{prefix}.csv"
header = "iterarion;double;triple"

clines = count_lines(results_filename)

if(clines == 0):
    for line in header:
        add_line(results_filename, line, 0)

clines = count_lines(results_filename)
N_ITERAZIONS = 10000 - clines + 1 #prima riga di testata


################
### GET DATA ###
################
# this method returns two geo-dataframe, the first contains the double or triple buindings, the second contains all the historical addreses
historical_buildings_gdf, total_historical_gdf = get_data(TORINO=TORINO)

#########################################
### INSTANTIATE THE GDF FOR ARPA DATA ###
#########################################
BUILDING_PATH = "shp/residenzialeNonTorino.csv" #ARPA data - not available in the library
if TORINO:
    BUILDING_PATH = "shp/residenzialeTorino.csv" #ARPA data - not available in the library

buildings_gdf = pd.read_csv(BUILDING_PATH)
buildings_gdf.USO_DESC.replace(np.NaN, '', inplace=True)

buildings_gdf.ID_EDIF = buildings_gdf.ID_EDIF.astype(float).astype(int)
buildings_gdf.POP_INT = buildings_gdf.POP_INT.astype(float).astype(int)

buildings_gdf = buildings_gdf[buildings_gdf.POP_INT > 0]

buildings_gdf = buildings_gdf[buildings_gdf['USO_DESC'].isin(
    [
        'residenziale', 'basso fabbricato generico', 'residenziale; commerciale',
        'residenziale; non conosciuto', 'non conosciuto; residenziale', 'residenziale; servizio pubblico',
        'residenziale; amministrativo'
    ]
)]

##################
### MONTACARLO ###
##################
def monte_carlo(historical, buildings_gdf, clines=0, filename=''):
    # create array containing building id as many times as many people live in it
    buildings_array = np.repeat(buildings_gdf['ID_EDIF'].values, buildings_gdf['POP_INT'].values).tolist()

    # calculating how many times patients have moved house in their lifetime
    n_patients = len(historical['codals_parals'].unique())
    mean_change_house = len(historical['codals_parals']) / n_patients

    # create array that allows you to create same distribution of home changes
    print(f"There were {n_patients} who changed homes on average {mean_change_house} times")
    n_change_house = generate_closest_array(mean_change_house, 5)

    total_d_buildings = []
    total_t_buildings = []
    patients_array = np.arange(n_patients)

    for iteration in np.arange(N_ITERAZIONS):
        # start MonteCarlo iterarion
        # create array with the random choosen buildings
        buildings = []
        # select random buildings for each patients
        for patients in patients_array:
            change_house_times = random.sample(n_change_house, 1)[0]
            patient_buildings = random.sample(buildings_array, change_house_times)
            buildings = buildings + patient_buildings
        c = Counter(buildings).items()

        double_iteration = len(list({k: v for k, v in c if v == 2}))
        triple_iteration = len(list({k: v for k, v in c if v >= 3}))
        total_d_buildings.append(double_iteration)
        total_t_buildings.append(triple_iteration)

        line = f'{clines};{double_iteration};{triple_iteration}'
        add_line(filename=filename, line=line, count_lines=clines)

        clines = clines + 1

    # end MonteCarlo iterarion

    monte_carlo_df = pd.DataFrame({
        'total_d_buildings' : np.array(total_d_buildings),
        'total_t_buildings' : np.array(total_t_buildings),
    })

    return monte_carlo_df


monte_carlo_df = monte_carlo(total_historical_gdf, buildings_gdf, clines=clines, filename=results_filename)

monte_carlo_df.to_csv(f'{prefix}montecarloResults.csv', sep=';')

mu = monte_carlo_df.total_d_buildings.mean()
sigma = monte_carlo_df.total_d_buildings.std()

###############
### RESULTS ###
###############
value = len(historical_buildings_gdf[historical_buildings_gdf['n_after_removing_mutation_and_familial'] == 2])
z = (value - mu) / sigma
p_values = stats.norm.sf(abs(z))*2 #twosided

print(f"In {prefix}, there are {value} condominiums that are ONLY double.")
print(f"Monte Carlo gives an average of {monte_carlo_df.total_d_buildings.mean()} double buildings with STD {monte_carlo_df.total_d_buildings.std()}")
print(f"This value is away from the mean {z} deviations and pvalue of {p_values}")

mu = monte_carlo_df.total_t_buildings.mean()
sigma = monte_carlo_df.total_t_buildings.std()

value = len(historical_buildings_gdf[historical_buildings_gdf['n_after_removing_mutation_and_familial'] >= 3])
z = (value - mu) / sigma
p_values = stats.norm.sf(abs(z))*2 #twosided

print(f"In {prefix}, there are {value} condominiums that are triple or more.")
print(f"Monte Carlo gives an average of {monte_carlo_df.total_t_buildings.mean()} triple or more buildings with STD {monte_carlo_df.total_t_buildings.std()}")
print(f"This value is away from the mean {z} deviations and pvalue of {p_values}")
