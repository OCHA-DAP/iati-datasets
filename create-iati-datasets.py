import config
import ckanapi, copy, json, logging, os, re, time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create-iati-datasets")

# How many seconds do we pause between API calls?
PAUSE = 2

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

#
# Iterate through each country and create or update an IATI dataset
#
for country in countries['data']:

    # Skip if there's no ISO2 code
    if not country['iso2']:
        logger.warning("skipping %s (no ISO2 code)", iso2)
        continue

    # Grab the country tombstone data
    name = country['label']['default']
    iso2 = country['iso2'].lower()
    iso3 = country['iso3'].lower()

    # Skip if the country is not in HDX
    if not iso3 in groups:
        logger.warning("skipping %s (%s)", name, iso2)
        continue

    # Copy the template
    package = copy.deepcopy(template)

    # Do the template substitutions for this country
    package["name"] = package["name"].replace("{{ISO3}}", iso3)
    for key in ["title", "notes"]:
        package[key] = package[key].replace("{{NAME}}", name)
    for group in package["groups"]:
        group["name"] = group["name"].replace("{{ISO3}}", iso3)
    for resource in package["resources"]:
        for key in ["description", "name"]:
            resource[key] = resource[key].replace("{{NAME}}", name)
        resource["url"] = resource["url"].replace("{{ISO2}}", iso2)

    # Do we have an existing package?
    try:
        old = ckan.action.package_show(id=package["name"])
        logger.info("Updating existing dataset %s", package["name"])
        ckan.call_action('package_update', package)
    except ckanapi.errors.NotFound:
        logger.info("Creating new dataset %s", package["name"])
        ckan.call_action('package_create', package)

    # Give CKAN a chance to catch its breath
    time.sleep(PAUSE)
