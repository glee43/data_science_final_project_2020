import sqlite3
import csv
import pandas as pd
from pandas import DataFrame


'''
    Define the field the population object has in the data
'''

conn = sqlite3.connect('../data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "population";')
conn.commit()

# Create population table
# NOTE: the first two rows are titles of what the data contains
c.execute(
    'CREATE TABLE population( \
        state varchar(100), \
        target_geo_id_1 varchar(100) primary key, \
        target_geo_id_2 int, \
        geographic_area varchar(100), \
        total_population int, \
        housing_units int, \
        total_square_miles float, \
        water_square_miles float, \
        land_square_miles float, \
        land_population_density float, \
        housing_population_density float \
    )')
conn.commit()


# get rid of the revision field and returns a float
def getFloat(field):
    # print("word")
    # print(field)

    # when the data doesn't exist
    if "(X)" in field:
        return -1

    if "(" in field:
        field = field.split("(")
        # print(field)
        # print(field[0])
        field = float(field[0])
    # when the data doesn't exist
    if "(X)" in field:
        return -1.0
    return field


def getInt(field):
    # when the data doesn't exist
    if "(X)" in field:
        return -1

    if "(" in field:
        field = field.split("(")
        field = int(field[0])

    return field


def read_data(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            c.execute('INSERT INTO population VALUES \
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (row[2], row[3], getInt(row[4]), row[6], getInt(row[7]),
                       getInt(row[8]), getFloat(row[9]), getFloat(row[10]),
                       getFloat(row[11]), getFloat(row[12]), getFloat(row[13])))
            conn.commit()


read_clients = read_data('../data/population.csv')
# Insert the values from the csv file into the table 'CLIENTS'

print("finished")
