import sqlite3
import csv
import re
import json

'''
    Creates the housing table and add it to data.db
    Populates it using data from data/housing_city_monthly.csv
'''

conn = sqlite3.connect('../data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "housing";')
conn.commit()

# Create gunviolence table
# NOTE: the first two rows are titles of what the data contains
c.execute(
        'CREATE TABLE housing( \
        city varchar(100) , \
        state varchar(100), \
        county varchar(100), \
        prices varchar(8000), \
        PRIMARY KEY (city, state, county) \
    )')
conn.commit()


def getInt(field):
    # when the data doesn't exist
    if field == None or field == "":
        return None
    return int(field)

def stripSpecial(s):
    # used to make all town,city, and county names
    # lower case and only a-z characters so that they
    # are easier to match with dirty data
    if s == None:
        return None
    s = s.lower()
    rex = re.compile(("[^a-z]"))
    stripped = re.sub(rex, "", s)
    return stripped


def read_data(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        first = True
        headers = ["regionID", "city", "state", "metro", "county", "sizeRank"]
        dates = []
        i = 1
        for row in reader:  
            # the first row just has field names and year/month values
            if first:
                # headers = row[0:6]
                for date in row[6:]:
                    # year = int(date.split("-")[0])
                    # month = int(date.split("-")[1])
                    dates.append(date)
                first = False
            else:
                # print(i)
                i += 1
                # create dicts for field names and monthly price data
                fields = dict(zip(headers, row[0:6]))
                # print(fields["city"])
                prices = dict(zip(dates, [getInt(x) for x in row[6:]]))
                c.execute('INSERT INTO housing VALUES \
                    (?, ?, ?, ?)',
                        (stripSpecial(fields["city"]),
                        stripSpecial(fields["state"]),
                        stripSpecial(fields["county"]),
                        json.dumps(prices)))
                conn.commit()


read_data('../data/housing_city_monthly.csv')

print("Finished reading data from housing_city_monthly.csv to the database.")