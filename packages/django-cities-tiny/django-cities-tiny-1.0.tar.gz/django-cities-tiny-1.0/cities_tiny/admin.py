from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.contrib import admin

from cities_tiny.models import Country, AdminDivision, City

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ascii', 'code2', 'code3', 'continent', 'geoname_id')
    search_fields = ('name', 'name_ascii', 'code2', 'code3', 'geoname_id')
    list_filter = ('continent',)
admin.site.register(Country, CountryAdmin)

class AdminDivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ascii', 'country', 'level', 'geoname_id')
    search_fields = ('name', 'name_ascii', 'geoname_id')
    list_filter = ('country', 'level')
    raw_id_fields = ('parent',)
admin.site.register(AdminDivision, AdminDivisionAdmin)

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ascii', 'country', 'population', 'geoname_id')
    search_fields = ('name', 'name_ascii', 'geoname_id')
    list_filter = ('country',)
    raw_id_fields = ('admins',)
    readonly_fields = ('display_admins',)

    def display_admins(self, obj):
	result = []
	for admin in obj.admins.all():
	    href = reverse('admin:cities_tiny_admindivision_change', args=[admin.pk])
	    html = '<a href="%s">%s</a>' % (escape(href), escape(admin))
	    result.append(html)
	return ', '.join(result)
    display_admins.allow_tags = True
    display_admins.short_description = _("Administrative zones")

admin.site.register(City, CityAdmin)
