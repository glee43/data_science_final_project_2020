# CS1951A Final Project - Team Lee-Lee-Ho-Ho

[Shared drive link](https://drive.google.com/drive/u/0/folders/0AFUpf_youHivUk9PVA)

## Repo Structure

### data [folder]: contains the raw data format

### scripts [folder]: contains scripts for loading data

-   population.py : reads in US population data into the population table in data.db

### data.db [database]: the actual sqlite database

-   gunviolence: contains

| field                       | type                            | description                                                                   | required? |
| --------------------------- | ------------------------------- | ----------------------------------------------------------------------------- | --------- |
| incident_id                 | int                             | gunviolencearchive.org ID for incident                                        | yes       |
| date                        | str                             | date of occurrence                                                            | yes       |
| state                       | str                             | state where the occurance happened                                            | yes       |
| city_or_county              | str                             | where the incident occured (could be used to join with population data)       | yes       |
| address                     | str                             | address where incident took place                                             | yes       |
| n_killed                    | int                             | number of people killed                                                       | yes       |
| n_injured                   | int                             | number of people injured                                                      | yes       |
| incident_url                | str                             | link to gunviolencearchive.org webpage containing details of incident         | yes       |
| source_url                  | str                             | link to online news story concerning incident                                 | no        |
| incident_url_fields_missing | bool                            | ignore, always False                                                          | yes       |
| congressional_district      | int                             | integer for the congressional district                                        | no        |
| gun_stolen                  | str w/ encoding: dict[int, str] | key: gun ID, value: 'Unknown' or 'Stolen'                                     | no        |
| gun_type                    | str w/ encoding: dict[int, str] | key: gun ID, value: description of gun type                                   | no        |
| incident_characteristics    | str w/ encoding: list[str]      | list of incident characteristics                                              | no        |
| latitude                    | float                           | latitude value for the incident                                               | no        |
| location_description        | str                             | description of location where incident took place                             | no        |
| longitude                   | float                           | longitude value for the incident                                              | no        |
| n_guns_involved             | int                             | number of guns involved                                                       | no        |
| notes                       | str                             | additional notes about the incident                                           | no        |
| participant_age             | str w/ encoding: dict[int, int] | key: participant ID, value: age                                               | no        |
| participant_age_group       | str w/ encoding: dict[int, str] | key: participant ID, value: description of age group, e.g. 'Adult 18+'        | no        |
| participant_gender          | str w/ encoding: dict[int, str] | key: participant ID, value: 'Male' or 'Female'                                | no        |
| participant_name            | str w/ encoding: dict[int, str] | key: participant ID, value: name (might be missing)                           | no        |
| participant_relationship    | str w/ encoding: dict[int, str] | key: participant ID, value: relationship of participant to other participants | no        |
| participant_status          | str w/ encoding: dict[int, str] | key: participant ID, value: 'Arrested', 'Killed', 'Injured', or 'Unharmed'    | no        |
| participant_type            | str w/ encoding: dict[int, str] | key: participant ID, value: 'Victim' or 'Subject-Suspect'                     | no        |
| sources                     | str w/ encoding: list[str]      | links to online news stories concerning incident                              | no        |
| state_house_district        | int                             | congressional house district value                                            | no        |
| state_senate_district       | int                             | congressional senate district value                                           | no        |

-   population: contains the fields

| field                      | type  | description                                                                                             | required? |
| -------------------------- | ----- | ------------------------------------------------------------------------------------------------------- | --------- |
| state                      | str   | population state                                                                                        | yes       |
| target_geo_id_1            | str   | US Census location ID (https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html) | yes       |
| target_geo_id_2            | int   | Secondary US Census location ID (see above)                                                             | yes       |
| geographic_area            | str   | actual city, county, or state (might need additional partioning to use)                                 | yes       |
| total_population           | int   | number of total population for the area                                                                 | no        |
| housing_units              | int   | number of housing units in the area                                                                     | no        |
| total_square_miles         | float | total square mile of the area                                                                           | no        |
| water_square_miles         | float | number of square miles that is water in the area                                                        | no        |
| land_square_miles          | float | nember of square miles that is land in the area                                                         | no        |
| land_population_density    | float | population density with respect to land mass                                                            | no        |
| housing_population_density | float | population density with respect to housing                                                              | no        |
