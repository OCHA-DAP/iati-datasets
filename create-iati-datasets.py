import config
import ckanapi, json, os, re

# Get script directory (for loading local JSON files)
directory = os.path.dirname(os.path.realpath(__file__))

# Load countries from disk
with open(os.path.join(directory, "countries.json"), "r") as input:
    countries = json.load(input)

# Load template from disk
with open(os.path.join(directory, "dataset-template.json"), "r") as input:
    template = json.load(input)

# Open CKAN connection
ckan = ckanapi.RemoteCKAN(config.CONFIG['ckanurl'], apikey=config.CONFIG['apikey'], user_agent=config.CONFIG.get('user_agent', None))

# Load groups from CKAN
groups = ckan.action.group_list()


print(template)
