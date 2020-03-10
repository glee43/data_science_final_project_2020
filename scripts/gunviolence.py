import sqlite3
import csv

'''
    Creates the gunviolence table and add it to data.db
'''

conn = sqlite3.connect('../data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "gunviolence";')
conn.commit()

# Create gunviolence table
# NOTE: the first two rows are titles of what the data contains
c.execute(
    'CREATE TABLE gunviolence( \
        incident_id int primary key, \
        date varchar(100) , \
        state varchar(100), \
        city_or_county varchar(100), \
        address varchar(100), \
        n_killed int, \
        n_injured int, \
        incident_url varchar(10000), \
        source_url varchar(10000), \
        incident_url_fields_missing bool, \
        congressional_district int \
        gun_stolen varchar(10000), \
        gun_type varchar(10000), \
        incident_characteristics varchar(10000), \
        latitude float, \
        location_description varchar(10000), \
        longitude float, \
        n_guns_involved int, \
        notes varchar(10000), \
        participant_age varchar(10000), \
        participant_age_group varchar(10000), \
        participant_gender varchar(10000), \
        participant_name varchar(10000), \
        participant_relationship varchar(10000), \
        participant_status varchar(10000), \
        participant_type varchar(10000), \
        sources varchar(10000), \
        state_house_district int, \
        state_senate_district int \
    )')
conn.commit()


# get rid of the revision field and returns a float
def getFloat(field):
    # when the data doesn't exist
    if field == None or field == "":
        return None

    return float(field)


def getInt(field):
    # when the data doesn't exist
    if field == None or field == "":
        return None
    return int(field)


def read_data(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            if i == 0:
                i = 1
            else:
                c.execute('INSERT INTO gunviolence VALUES \
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                          (getInt(row[0]), row[1], row[2], row[3],
                           (row[4]), getInt(row[5]), getInt(row[6]),
                              row[7], (row[8]), (row[9]), getInt(row[10]),
                              (row[11]), (row[12]), (row[13]),
                              getFloat(row[14]), (row[15]), getFloat(row[16]),
                              getInt(row[17]), (row[18]), (row[19]),
                              (row[20]), (row[21]), (row[22]),
                              (row[23]), (row[24]), (row[25]),
                              (row[26]), (row[27])
                           ))
                conn.commit()


read_data('../data/stage3.csv')

print("Finished reading data from gunviolence1.csv to the database.")
