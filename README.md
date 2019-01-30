# Script to create filter IATI datasets in a CKAN instance

## Prerequisites

* Python3
* ckancrawler

## Instructions

1. Copy the file config.py.TEMPLATE to config.py and fill in the
   fields.
2. Load the requirements ``pip3 install -r requirements.txt``
3. Execute the command ``python3 create-iati-datasets.py``


## Data sources

Country codes and names come courtesy of OCHA Digital Services. The
original data is here:
https://data.humdata.org/dataset/countries-and-territories-beta

IATI financial data comes from D-Portal: http://www.d-portal.org
