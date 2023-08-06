from django.conf import settings

COUNTRY_SOURCES = getattr(settings, 'CITIES_TINY_COUNTRY_SOURCES', [
    'http://download.geonames.org/export/dump/countryInfo.txt',
    ])

ADMIN_SOURCES = getattr(settings, 'CITIES_TINY_ADMIN_SOURCES', [
    'http://download.geonames.org/export/dump/admin1CodesASCII.txt',
    'http://download.geonames.org/export/dump/admin2Codes.txt',
    ])

CITY_SOURCES = getattr(settings, 'CITIES_TINY_CITY_SOURCES', [
    'http://download.geonames.org/export/dump/cities15000.zip',
    ])

ALTERNATE_NAMES = getattr(settings, 'CITIES_TINY_ALTERNATE_NAMES', [
    'http://download.geonames.org/export/dump/alternateNames.zip',
    ])

# If enabled the name field of geo objects will be translated using strings from
# ALTERNATE_NAMES and according to LANGUAGES
ENABLE_I18N = getattr(settings, 'CITIES_TINY_ENABLE_I18N', True)

# List of 2-letter language codes for translation. Many records in
# alternateNames.txt don't have a language code set, so if you add 'like-LL', then
# strings without language code but with matched characters will be also used.
LANGUAGES = getattr(settings, 'CITIES_TINY_LANGUAGES', [
    settings.LANGUAGE_CODE[:2],
    'like-' + settings.LANGUAGE_CODE[:2],
    ])

# Import only objects in listed countries. List of 2-letter country code in
# uppercase. If None then all countries will be imported.
COUNTRIES = getattr(settings, 'CITIES_TINY_COUNTRIES', None)

# Minimum city population to import.
CITY_MIN_POPULATION = getattr(settings, 'CITIES_TINY_CITY_MIN_POPULATION', 15000)

# Maximum administrative division zone level to import.
ADMIN_MAX_LEVEL = getattr(settings, 'CITIES_TINY_ADMIN_MIN_LEVEL', 2)

# Download directory.
DATA_DIR = getattr(settings, 'CITIES_TINY_DATA_DIR', 'data')
