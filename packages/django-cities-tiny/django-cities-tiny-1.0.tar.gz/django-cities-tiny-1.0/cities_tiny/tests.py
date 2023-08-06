import unittest
from django.core import management
from cities_tiny.models import Country, AdminDivision, City

class RefreshCommandTestCase(unittest.TestCase):
    def test_command(self):
	management.call_command('citiestinyrefresh', verbosity=2,
		force_import_all=True, force_all=False,
		force_import=[], force=[])
	self.assertEqual(Country.objects.count() > 0, True)
	self.assertEqual(AdminDivision.objects.count() > 0, True)
	self.assertEqual(City.objects.count() > 0, True)
