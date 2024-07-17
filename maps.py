import googlemaps
from mysql.connector import (connection)
from random import randint
from time import sleep

maps_key = '###'
tested = 1
cnx = connection.MySQLConnection(user='###', password='###',
                              host='127.0.0.1',
                              database='cresla_definitivo', auth_plugin='mysql_native_password')

cursor = cnx.cursor()

query = ("select * from historicals  ip where province in ('TO', 'CN', 'AL', 'VB', 'AT', 'NO', 'VC', 'BI', 'AO') and tested is null order by id")
cursor.execute(query)

patients = cursor.fetchall()
cursor.close()
g = googlemaps.Client(key=maps_key)

for patient in patients:
    localization = str(patient[2]) + ' ' + str(patient[3]) + ' ' + str(patient[4]) + ' ' + str(patient[5])  + ', Piemonte, Italia'
    print(localization)
    geocode_result = g.geocode(localization)
    print(localization)
    print(geocode_result)
    if(len(geocode_result)):
        geocode_result = geocode_result[0]
        lat = geocode_result['geometry']['location']['lat']
        lng = geocode_result['geometry']['location']['lng']

        cursor_patient = cnx.cursor()
        sql = f"UPDATE historicals SET tested={tested}, lat= " + str(lat) +", lng = " +str(lng) +" WHERE id = '" + str(patient[0]) + "'"
        print(sql)
        try:
            cursor_patient.execute(sql)
            cnx.commit()
        except:
            cnx.rollback()
        cursor_patient.close()
    sleep(randint(10, 20))