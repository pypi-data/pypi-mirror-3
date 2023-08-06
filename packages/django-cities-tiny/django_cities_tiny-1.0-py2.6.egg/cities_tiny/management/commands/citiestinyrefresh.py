import urllib
import time
import os
import logging
import zipfile
import optparse
from urlparse import urlsplit
import posixpath
import re

try:
    set
except NameError:
    from sets import Set as set     # For Python 2.3

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db import transaction
from django.utils.encoding import force_unicode

from cities_tiny.models import Country, AdminDivision, City
from cities_tiny.settings import *

log = logging.getLogger('cities_light')
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

lang_valid_chars = {
	'ru': re.compile(ur'^[\u0400-\u04ff-]+$'),
	'uk': re.compile(ur'^[\u0400-\u04ff-]+$'),
	'by': re.compile(ur'^[\u0400-\u04ff-]+$'),
	}

class Command(BaseCommand):
    args = '''
[--force-all] [--force-import-all \\]
                              [--force-import allCountries.txt FR.zip ...] \\
                              [--force allCountries.txt FR.zip ...]
    '''.strip()
    help = '''
Download all files in CITIES_TINY_COUNTRY_SOURCES if they were updated or if 
--force-all option was used.
Import country data if they were downloaded or if --force-import-all was used.

Same goes for CITIES_TINY_CITY_SOURCES.

It is possible to force the download of some files which have not been updated
on the server:

    manage.py --force FR.zip countryInfo.txt

It is possible to force the import of files which weren't downloaded using the 
--force-import option:

    manage.py --force-import FR.zip countryInfo.txt
    '''.strip()


    option_list = BaseCommand.option_list + (
        optparse.make_option('--force-import-all', action='store_true', default=False,
            help='Import even if files are up-to-date.'
        ),
        optparse.make_option('--force-all', action='store_true', default=False,
            help='Download and import if files are up-to-date.'
        ),
        optparse.make_option('--force-import', action='append', default=[],
            help='Import even if filenames matching FORCE_IMPORT are up-to-date.'
        ),
        optparse.make_option('--force', action='append', default=[],
            help='Download and import if filenames matching FORCE are up-to-date.'
        ),
    )

    def handle(self, *args, **options):
	def prepare_file(url):
	    basename = posixpath.basename(urlsplit(url)[2])
            dest_path = os.path.join(DATA_DIR, basename)
            
            force = options['force_all'] or basename in options['force']
            downloaded = self.download(url, dest_path, force)
            
            if posixpath.splitext(basename)[1] == '.zip':
                basename2 = basename.replace('.zip', '.txt')
                dest_path2 = os.path.join(DATA_DIR, basename2)
		if (not os.path.exists(dest_path2) or
			os.stat(dest_path2).st_mtime < os.stat(dest_path).st_mtime):
		    self.extract(dest_path, basename2)
		    downloaded = True
                dest_path = dest_path2
	    return dest_path, downloaded

	if 'verbosity' in options:
	    log_level = min(50, max(10,
		10 + 20 * (2 - int(options['verbosity']))))
	    log.setLevel(log_level)
	    log.addHandler(log_handler)

        if not os.path.exists(DATA_DIR):
            log.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

	alt_names = {}
	if ENABLE_I18N:
	    for url in ALTERNATE_NAMES:
		file_name, downloaded = prepare_file(url)
                log.info('Importing %s' % file_name)
		self.import_alt_names(file_name, alt_names)

	sources = list(COUNTRY_SOURCES) + list(ADMIN_SOURCES) + list(CITY_SOURCES)
        for url in sources:
	    file_name, downloaded = prepare_file(url)
            force_import = options['force_import_all'] or \
                posixpath.basename(file_name) in options['force_import']
            if downloaded or force_import:
                if url in COUNTRY_SOURCES:
		    log.info('Importing countries from %s' % file_name)
                    self.country_import(file_name, alt_names)
                elif url in ADMIN_SOURCES:
		    log.info('Importing admin division zones from %s' % file_name)
                    self.admin_import(file_name, alt_names)
                if url in CITY_SOURCES:
		    log.info('Importing admin division zones from %s' % file_name)
                    self.admin_city_import(file_name, alt_names)
		    log.info("Updating admin zone hierarchy")
		    self.update_admin_hierarchy()
		    log.info('Importing cities from %s' % file_name)
                    self.city_import(file_name, alt_names)
  
    def download(self, url, path, force=False):
        remote_file = urllib.urlopen(url)
        remote_time = time.strptime(remote_file.headers['last-modified'], 
            '%a, %d %b %Y %H:%M:%S %Z')
        remote_size = int(remote_file.headers['content-length'])

        if os.path.exists(path) and not force:
            local_time = time.gmtime(os.path.getmtime(path))
            local_size = os.path.getsize(path)

            if local_time >= remote_time and local_size == remote_size:
                log.warning('Assuming local download is up to date for %s' % url)
                return False

        log.info('Downloading %s into %s' % (url, path))
	
	local_file = open(path, 'wb')
	chunk = remote_file.read()
	while chunk:
	    local_file.write(chunk)
	    chunk = remote_file.read()
	local_file.close()
        
        return True

    def extract(self, zip_path, file_name):
        destination = os.path.join(DATA_DIR, file_name)
        
        log.info('Extracting %s from %s into %s' % (file_name, zip_path, destination))

	zip_file = zipfile.ZipFile(zip_path)
        dest_file = open(destination, 'wb')
	dest_file.write(zip_file.read(file_name))
	dest_file.close()
	zip_file.close()

    def parse(self, file_path):
        file = open(file_path, 'r')
        line = True

        while line:
            line = file.readline().strip()
            
            if len(line) < 1 or line[0] == '#':
                continue

            yield [e.strip() for e in line.split('\t')]

    def import_alt_names(self, file_path, alt_names=None):
	if alt_names is None:
	    alt_names = {}

	languages = set([x for x in LANGUAGES if not x.startswith('like-')])
	like_languages = set([x for x in LANGUAGES if x.startswith('like-')])

        for row in self.parse(file_path):
	    alt_name_id, geoname_id, lang, name = row[:4]
	    name = name.decode('utf-8')
	    is_preferred = len(row) >= 5 and row[4] or ''
	    is_short = len(row) >= 6 and row[5] or ''
	    like_lang = None

	    if is_short:
		continue

	    if lang:
		if lang not in languages:
		    continue
	    else:
		for ll in like_languages:
		    try:
			regex = lang_valid_chars[ll.replace('like-', '')]
		    except KeyError:
			continue
		    if regex.match(name):
			lang = ll
			break
		if not lang:
		    continue

	    geoname_id = int(geoname_id)
	    alt_names.setdefault(lang, {})
	    if is_preferred or geoname_id not in alt_names[lang]:
		alt_names[lang][geoname_id] = name
	return alt_names

    def get_translation(self, geoname_id, alt_names):
	for lang in LANGUAGES:
	    try:
		return alt_names[lang][geoname_id]
	    except KeyError:
		pass
	return None

    def get_country_by_code2(self, code2):
        if not hasattr(self, '_country_code2_map'):
            self._country_code2_map = {}
	try:
	    return self._country_code2_map[code2]
	except KeyError:
	    try:
		self._country_code2_map[code2] = Country.objects.get(code2=code2)
	    except Country.DoesNotExist:
		log.warning("Country with code2 %s does not exists", code2)
		return None
        return self._country_code2_map[code2]

    def get_admin_by_code_list(self, country, code_list):
        if not hasattr(self, '_admin_code_map'):
            self._admin_code_map = {}
	code_list = tuple(code_list)
	try:
	    return self._admin_code_map[country.pk][code_list]
	except KeyError:
	    self._admin_code_map.setdefault(country.pk, {})
	    try:
		self._admin_code_map[country.pk][code_list] = AdminDivision.objects.by_code_list(
			country, code_list)
	    except AdminDivision.DoesNotExist:
		log.warning("Admin division zone with codes %s does not exists",
			'.'.join(code_list))
		return None
        return self._admin_code_map[country.pk][code_list]

    def country_import(self, file_path, alt_names):
        for row in self.parse(file_path):
	    code2 = row[0]
	    name = name_ascii = row[4]
	    geoname_id = row[16] and int(row[16]) or None

	    if COUNTRIES is not None:
		if code2 not in COUNTRIES:
		    continue

	    if ENABLE_I18N and geoname_id:
		name = self.get_translation(geoname_id, alt_names) or name

	    if geoname_id:
		try:
		    country = Country.objects.get(geoname_id=geoname_id)
		except Country.DoesNotExist:
		    country = None
	    if country is None:
		try:
		    country = Country.objects.get(geoname_id__isnull=True,
			    code2=code2)
		except Country.DoesNotExist:
		    country = Country(code2=code2, allow_update=True)
	    
	    if country.allow_update:
		country.geoname_id = geoname_id
		country.name = name
		country.name_ascii = name_ascii
		country.code2 = code2
		country.code3 = row[1]
		country.continent = row[8]
		try:
		    sid = transaction.savepoint()
		    country.save()
		    transaction.savepoint_commit(sid)
		except IntegrityError, e:
		    log.warning("Country IntegrityError: %s", str(e))
		    transaction.savepoint_rollback(sid)

    def admin_import(self, file_path, alt_names):
        for row in self.parse(file_path):
	    admin_codes = row[0].split('.')
	    name = row[1].decode('utf-8')
	    name_ascii = row[2]
	    geoname_id = int(row[3])
	    code2 = admin_codes.pop(0)
	    population = 0

	    if COUNTRIES is not None:
		if code2 not in COUNTRIES:
		    continue
	    level = len(admin_codes)

	    if level > ADMIN_MAX_LEVEL:
		continue

	    country = self.get_country_by_code2(code2)
	    if country is None:
		continue

	    if ENABLE_I18N:
		name = self.get_translation(geoname_id, alt_names) or name

	    admin1 = len(admin_codes) >= 1 and admin_codes[0] or ''
	    admin2 = len(admin_codes) >= 2 and admin_codes[1] or ''
	    admin3 = len(admin_codes) >= 3 and admin_codes[2] or ''
	    admin4 = len(admin_codes) >= 4 and admin_codes[3] or ''

            try:
                obj = AdminDivision.objects.get(geoname_id=geoname_id)
            except AdminDivision.DoesNotExist:
		try:
		    obj = AdminDivision.objects.get(geoname_id__isnull=True, country=country,
			    admin1=admin1, admin2=admin2, admin3=admin3, admin4=admin4)
		except AdminDivision.DoesNotExist:
		    obj = AdminDivision(allow_update=True, allow_name_update=True)

	    if obj.allow_name_update:
		obj.name = name
	    if obj.allow_update:
		obj.geoname_id = geoname_id
		obj.name_ascii = name_ascii
		obj.country = country
		obj.admin1 = admin1
		obj.admin2 = admin2
		obj.admin3 = admin3
		obj.admin4 = admin4
		obj.population = population
		obj.level = level
	    if obj.allow_update or obj.allow_name_update:
		try:
		    sid = transaction.savepoint()
		    obj.save()
		    transaction.savepoint_commit(sid)
		except IntegrityError, e:
		    log.warning("AdminDivision IntegrityError: %s: country=%s, "
			    "admin1=%s, admin2=%s, admin3=%s, admin4=%s",
			    str(e), repr(obj.country.name_ascii),
			    repr(admin1), repr(admin2), repr(admin3), repr(admin4))
		    transaction.savepoint_rollback(sid)

    def admin_city_import(self, file_path, alt_names):
        for row in self.parse(file_path):
	    geoname_id = int(row[0])
	    name = row[1].decode('utf-8')
	    name_ascii = row[2]
	    feature_code = row[7]
	    code2 = row[8]
	    admin1, admin2, admin3, admin4 = row[10:14]
	    population = int(row[14])

	    if feature_code not in ('ADM1', 'ADM2', 'ADM3', 'ADM4'):
		continue

	    if COUNTRIES is not None:
		if code2 not in COUNTRIES:
		    continue

	    level = 0
	    if (feature_code.startswith('ADM') and len(feature_code) == 4
		    and feature_code[3].isdigit()):
		level = int(feature_code[3])

	    if level > ADMIN_MAX_LEVEL:
		continue

	    country = self.get_country_by_code2(code2)
	    if country is None:
		continue

	    if ENABLE_I18N:
		name = self.get_translation(geoname_id, alt_names) or name

            try:
                obj = AdminDivision.objects.get(geoname_id=geoname_id)
            except AdminDivision.DoesNotExist:
		try:
		    obj = AdminDivision.objects.get(geoname_id__isnull=True,
			    country=country, admin1=admin1, admin2=admin2, admin3=admin3, admin4=admin4)
		except AdminDivision.DoesNotExist:
		    obj = AdminDivision(allow_update=True, allow_name_update=True)

	    if obj.allow_name_update:
		obj.name = name
	    if obj.allow_update:
		obj.geoname_id = geoname_id
		obj.name_ascii = name_ascii
		obj.country = country
		obj.admin1 = admin1
		obj.admin2 = admin2
		obj.admin3 = admin3
		obj.admin4 = admin4
		obj.population = population
		obj.level = level
	    if obj.allow_update or obj.allow_name_update:
		try:
		    sid = transaction.savepoint()
		    obj.save()
		    transaction.savepoint_commit(sid)
		except IntegrityError, e:
		    log.warning("AdminDivision IntegrityError: %s: country=%s, "
			    "admin1=%s, admin2=%s, admin3=%s, admin4=%s",
			    str(e), repr(obj.country.name_ascii),
			    repr(admin1), repr(admin2), repr(admin3), repr(admin4))
		    transaction.savepoint_rollback(sid)

    def update_admin_hierarchy(self):
	for obj in AdminDivision.objects.filter(level__gt=1, allow_update=True):
	    code_list = obj.get_code_list()[:-1]
	    level = obj.level - 1
	    while code_list:
		obj.parent = self.get_admin_by_code_list(
			obj.country, code_list)
		if obj.parent is not None:
		    if obj.parent.level != level:
			obj.parent = None
		if obj.parent is not None:
		    break
		code_list.pop()
		level -= 1
	    obj.save()

    def city_import(self, file_path, alt_names):
        for row in self.parse(file_path):
	    geoname_id = int(row[0])
	    name = row[1].decode('utf-8')
	    name_ascii = row[2]
	    feature_code = row[7]
	    code2 = row[8]
	    admin1, admin2, admin3, admin4 = row[10:14]
	    population = int(row[14])

	    if not feature_code.startswith('PPL'):
		continue
	    if COUNTRIES is not None:
		if code2 not in COUNTRIES:
		    continue
	    if population < CITY_MIN_POPULATION:
		continue

	    country = self.get_country_by_code2(code2)
	    if country is None:
		continue

	    if ENABLE_I18N:
		name = self.get_translation(geoname_id, alt_names) or name

	    admin_codes = [admin1, admin2, admin3, admin4]
	    new_admin = None
	    while admin_codes:
		new_admin = self.get_admin_by_code_list(country, admin_codes)
		if new_admin is None:
		    admin_codes.pop()
		else:
		    break

            try:
		obj = City.objects.get(geoname_id=geoname_id)
            except City.DoesNotExist:
		if new_admin is not None:
		    kw = {'admins__pk': new_admin.pk}
		else:
		    kw = {}
		try:
		    obj = City.objects.get(geoname_id__isnull=True,
			    country=country, name_ascii=name_ascii, **kw)
		except City.DoesNotExist:
		    obj = City(allow_update=True, allow_name_update=True)

	    if obj.allow_name_update:
		obj.name = name
	    if obj.allow_update:
		obj.geoname_id = geoname_id
		obj.name_ascii = name_ascii
		obj.country = country
		obj.admin1 = admin1
		obj.admin2 = admin2
		obj.admin3 = admin3
		obj.admin4 = admin4
		obj.population = population
	    if obj.allow_update or obj.allow_name_update:
		try:
		    sid = transaction.savepoint()
		    obj.save()
		    transaction.savepoint_commit(sid)
		except IntegrityError, e:
		    log.warning("City IntegrityError: %s", str(e))
		    transaction.savepoint_rollback(sid)
		    continue
	    if obj.allow_update:
		while new_admin is not None:
		    try:
			old_admin = obj.admins.get(level=new_admin.level)
		    except AdminDivision.DoesNotExist:
			old_admin = None
		    if new_admin != old_admin:
			if old_admin is not None:
			    obj.admins.remove(old_admin)
			obj.admins.add(new_admin)
		    new_admin = new_admin.parent
