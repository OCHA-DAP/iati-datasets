""" July 2024 maintenance upgrades for IATI datasets on HDX.

- use TLS/SSL (https) for all upstream datasets
- add link to IATI geographical-precision codelist
- provide a distinct, human-readable name for downloads (e.g. "iati-gin.csv" rather than "data.csv")

"""

import config
import ckancrawler, json, logging, os, re

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("update-iati-datasets")
""" Object for logging info and error messages """

_directory = os.path.dirname(os.path.realpath(__file__))
""" Get script directory (for loading local JSON files) """

_iso_map = None
""" Map of ISO3 to ISO2 codes """


URL_PATTERN = "https://proxy.hxlstandard.org/data/download/iati-{iso3}.csv?url=https%3A%2F%2Fd-portal.org%2Fdquery%3Fform%3Dcsv%26human%3D1%26sql%3Dselect%2520*%2520from%2520act%2520left%2520join%2520country%2520using%2520%28aid%29%2520left%2520join%2520sector%2520using%2520%28aid%29%2520left%2520join%2520location%2520using%2520%28aid%29%2520where%2520status_code%253D2%2520and%2520country.country_code%253D%2527{iso2}%2527%2520and%2520day_end%2520%253E%253D%2520floor%28extract%28epoch%2520from%2520now%28%29%29%252F%2860*60*24%29%29%2520order%2520by%2520day_start%252C%2520day_end%252C%2520reporting&tagger-match-all=on&tagger-01-header=aid&tagger-01-tag=%23activity%2Bid&tagger-02-header=reporting&tagger-02-tag=%23org%2Breporting%2Bname&tagger-03-header=reporting_ref&tagger-03-tag=%23org%2Breporting%2Bcode&tagger-04-header=funder_ref&tagger-04-tag=%23org%2Bfunding%2Bcode&tagger-05-header=title&tagger-05-tag=%23activity%2Bname&tagger-07-header=status_code&tagger-07-tag=%23status&tagger-08-header=day_start&tagger-08-tag=%23date%2Bstart&tagger-09-header=day_end&tagger-09-tag=%23date%2Bend&tagger-11-header=description&tagger-11-tag=%23description&tagger-12-header=commitment&tagger-12-tag=%23value%2Bfunding%2Bcommitted%2Bm_usd&tagger-13-header=spend&tagger-13-tag=%23value%2Bfunding%2Bspent%2Bm_usd&tagger-21-header=country_code&tagger-21-tag=%23country%2Bname&tagger-22-header=country_percent&tagger-22-tag=%23indicator%2Bcountry_allocation%2Bpct&tagger-23-header=sector_group&tagger-23-tag=%23sector&tagger-24-header=sector_code&tagger-24-tag=%23subsector&tagger-25-header=sector_percent&tagger-25-tag=%23indicator%2Bsector_allocation%2Bpct&tagger-29-header=location_name&tagger-29-tag=%23location%2Bname&tagger-30-header=location_longitude&tagger-30-tag=%23geo%2Blon&tagger-31-header=location_latitude&tagger-31-tag=%23geo%2Blat&tagger-32-header=location_precision&tagger-32-tag=%23geo%2Bprecision%2Bcode&tagger-33-header=location_percent&tagger-33-tag=%23indicator%2Blocation_allocation%2Bpct&header-row=1&filter01=add&add-tag01=%23activity%2Burl&add-value01=%7B%7B%23activity%2Bid%7D%7D&add-header01=Activity+link&filter02=cut&cut-skip-untagged02=on&filter03=replace&replace-pattern03=http%3A%2F%2Fd-portal.org%2Fq.html%5C%3Faid%3D%28.%2B%29&replace-regex03=on&replace-value03=%5C1&replace-tags03=%23activity%2Bid&header-row=1"
""" Pattern for getting IATI activities for a country.

Format replacement params:
  iso3 - ISO3 code in lowercase
  iso2 - ISO2 code in uppercase

"""


def get_iso_map ():
    """ Construct a mapping table of ISO3 to ISO2 codes (all uppercase) """
    
    global _iso_map
    if _iso_map is None:
        with open(os.path.join(_directory, "countries.json"), "r") as input:
            countries = json.load(input)
        _iso_map = {}
        for entry in countries["data"]:
            _iso_map[entry["iso3"]] = entry["iso2"]
    return _iso_map


def update_dataset(crawler, iso3, package):
    """ Update a single IATI dataset """

    logger.info("Updating IATI activities for %s", iso3)

    iso2 = get_iso_map().get(iso3.upper())

    # Use the new HXL Proxy recipe as the URL, replacing params as needed
    package["url"] = URL_PATTERN.format(iso3=iso3, iso2=iso2)

    # Add a link to IATI geographical-precision dataset
    package["notes"] += "\n\nDefinitions for the geographical-precision codes are available at https://iatistandard.org/en/iati-standard/203/codelists/geographicalprecision/"

    # Update the dataset on HDX
    crawler.ckan.call_action('package_update', package)


def update_datasets (crawler):
    """ Iterate through all IATI datasets """

    # iterate through existing IATI datasets on HDX
    for package in crawler.packages(fq='organization:iati'):

        # check for expected format
        result = re.match(r'^iati-([a-z]{3})$', package['name'])

        if result:
            # last part of name is a lower-case ISO3 code
            iso3 = result.group(1)
            update_dataset(crawler, iso3, package)
        else:
            logger.warning("Skipping dataset %s \"%s\" (CKAN name in wrong format)", package['name'], package['title'])


#
# Command-line entry point
#

if __name__ == '__main__':
    crawler = ckancrawler.Crawler(config.CONFIG['ckanurl'], apikey=config.CONFIG['apikey'], user_agent=config.CONFIG['user_agent'])
    update_datasets(crawler)
    exit(0)
