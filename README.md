# CS1951A Final Project - Team Lee-Lee-Ho-Ho

[Shared drive link](https://drive.google.com/drive/u/0/folders/0AFUpf_youHivUk9PVA)

## Repo Structure

data: contains the raw data format

scripts: contains scripts for loading data

-   population.py : reads in US population data into the population table in data.db

data.db: the actual sqlite database

-   population: conatins the fields
    >
          state varchar(100),
          target_geo_id_1 varchar(100) primary key,
          target_geo_id_2 int,
          geographic_area varchar(100),
          total_population int,
          housing_units int,
          total_square_miles float,
          water_square_miles float,
          land_square_miles float,
          land_population_density float,
          housing_population_density float
    >
