from django.db import models
from django.utils.translation import ugettext_lazy as _

from cities_tiny.settings import *

CONTINENT_CHOICES = (
    ('OC', _(u'Oceania')),
    ('EU', _(u'Europe')),
    ('AF', _(u'Africa')),
    ('NA', _(u'North America')),
    ('AN', _(u'Antarctica')),
    ('SA', _(u'South America')),
    ('AS', _(u'Asia')),
)

class Country(models.Model):
    name = models.CharField(
	    verbose_name=_("country name"),
	    max_length=200, unique=True)
    name_ascii = models.CharField(
	    verbose_name=_("country name in ASCII"),
	    max_length=200, unique=True)
    code2 = models.CharField(
	    verbose_name=_("2-letter code"),
	    help_text=_("ISO-3166 2-letter country code."),
	    max_length=2, null=True, blank=True, unique=True)
    code3 = models.CharField(
	    verbose_name=_("3-letter code"),
	    help_text=_("ISO-3166 3-letter country code."),
	    max_length=3, null=True, blank=True, unique=True)
    continent = models.CharField(
	    verbose_name=_("continent"),
	    max_length=2, db_index=True, choices=CONTINENT_CHOICES)
    geoname_id = models.IntegerField(
	    verbose_name=_("Geoname ID"),
	    help_text=_("Object ID in the GeoNames.org database."),
	    null=True, blank=True, unique=True)
    allow_update = models.BooleanField(
	    verbose_name=_("allow update"),
	    help_text=_("Allow automatically override this info when updating."),
	    default=False)
    
    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class GeonameObject(models.Model):
    geoname_id = models.IntegerField(
	    verbose_name=_("Geoname ID"),
	    help_text=_("Object ID in the GeoNames.org database."),
	    null=True, blank=True, unique=True)
    name = models.CharField(
	    verbose_name=_("object name"),
	    max_length=200, db_index=True)
    name_ascii = models.CharField(
	    verbose_name=_("object name in ASCII"),
	    max_length=200, db_index=True, blank=True)
    country = models.ForeignKey(Country,
	    verbose_name=_("Country"))
    admin1 = models.CharField(
	    verbose_name=_("admin1 code"),
	    max_length=20, db_index=True, blank=True)
    admin2 = models.CharField(
	    verbose_name=_("admin2 code"),
	    max_length=80, db_index=True, blank=True)
    admin3 = models.CharField(
	    verbose_name=_("admin3 code"),
	    max_length=20, db_index=True, blank=True)
    admin4 = models.CharField(
	    verbose_name=_("admin4 code"),
	    max_length=20, db_index=True, blank=True)
    population = models.PositiveIntegerField(
	    verbose_name=_("population"))
    allow_update = models.BooleanField(
	    verbose_name=_("allow update"),
	    help_text=_("Allow automatically override this info when updating."),
	    default=False)
    allow_name_update = models.BooleanField(
	    verbose_name=_("allow name update"),
	    help_text=_("Allow automatically override name when updating."),
	    default=False)

    class Meta:
	abstract = True

    def __unicode__(self):
        return self.name

class AdminDivisionManager(models.Manager):
    def by_code_list(self, country, codes, level=None):
	kw = {'country': country}
	for i in range(1, 5):
	    if len(codes) > i-1:
		kw['admin%d' % i] = codes[i-1]
	    else:
		kw['admin%d' % i] = ''
	if level:
	    kw['level'] = level
	return self.get(**kw)

class AdminDivision(GeonameObject):
    level = models.PositiveIntegerField(
	    verbose_name=_("division level"),
	    blank=True, editable=False)
    parent = models.ForeignKey('self',
	    verbose_name=_("parent zone"),
	    related_name='children',
	    null=True, blank=True)
    objects = AdminDivisionManager()

    class Meta:
	verbose_name = _("Admin division zone")
        verbose_name_plural = _("Admin division zones")
	unique_together = (('country', 'admin1', 'admin2', 'admin3', 'admin4'),)
        ordering = ('name',)

    def get_code_list(self):
	codes = [self.admin1, self.admin2, self.admin3, self.admin4]
	codes = codes[:self.level]
	return codes

class City(GeonameObject):
    admins = models.ManyToManyField(AdminDivision,
	    verbose_name=_("Admin zones"),
	    related_name='cities', blank=True)

    class Meta:
	verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ('name',)
