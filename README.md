# wrangling-osm

Apply data wrangling techniques using Python to audit, clean-up and transform OpenStreetMap dataset from XML to CSV. Explore the CSV dataset using SQLite.

This project is part of the requirement to progress through Udacity's Data Analysis Nanodegree course.

The project calls for the extraction, investigation and cleaning of a dataset of a chosen area from OpenStreetMap. The dataset chosen is audited for problems with data quality, then cleaned programatically, and formatted to conform with a SQL database schema. SQLite is used to explore the cleaned dataset.

A final report (in HTML) captures key steps in the data wrangling process and interesting information from the OSM area extracted.   

#### data.py
Contains the main function to clean XML data by calling on sub-functions imported from  other Python files. Contains code to format the source XML data into CSV.

#### streetname.py
Contains functions to audit and clean errors in street names and names of highway elements. Functions are called by 'data.py'.

#### highway.py
Contains functions to audit for and clean 'highway=unclassified'.

#### schema.py
Used by Python's schema module to verify that data transformed by 'data.py' conforms to desired schema for import into SQL.

#### del_blankrows.py
Independent script to remove blank rows in CSV files generated by 'data.py' prior to import into SQL database. Directory containing the source CSV files (variable 'src_path') and output directory for the cleaned CSV files (variable 'dest_path') to be changed accordingly 
in the script. Filenames of cleaned CSV file are prefixed with 'clean_'.
