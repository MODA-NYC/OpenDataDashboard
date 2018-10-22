# Open Data Dashboard

This repository contains the scripts that run New York City's Open Data Dashboard. 

## Overview
The dashboard supports the operations of the NYC Open Data Team and Open Data Coordinators by describing key performance metrics of the NYC Open Data Portal.

The dashboard pulls data from three sources: 
1. Google Analytics Reporting API
2. NYC Open Data Asset Inventory Dataset through the Socrata API
3. NYC Open Data Help Desk Inquiries through the Screendoor API

## Dependencies
* Code is written in Python 3
* The dashboard was built using [Dash](https://dash.plot.ly/), a python package, version 0.22.0 

## File Descriptions
Non-Python files:

* README.md - Text file in markdown format describing the project and repository
* requirements.txt - Text file describing the packages required to run the dashboard

Python scripts: 

* dashboard.py - Integrates all data streams, creates all visualizations and draws the dashboard interface
* ga_api.py - Transforms the Google Analytics V4 API response data into usable dataframes
* ga_config.py - Configures Google Analytics API call 
* ga_functions.py - Parses and returns API data
* screendoor_api.py - Calls the Screendoor API and transforms the help desk inquiry responses into dataframes
* socrata_api.py - Calls the Socrata API and transforms the Asset Inventory data into the dataframes used in the "Asset Management" tables


## Acknowledgments
* Erik Driessen's [quick_gaapi](https://github.com/edriessen/quick_gaapi)
