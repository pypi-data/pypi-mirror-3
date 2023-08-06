import os
import unittest

from django.core import management

from cities_tiny.models import City
from metro_tiny.models import MetroLine, MetroStation

class RefreshCommandTestCase(unittest.TestCase):
    def test_command(self):
	management.call_command('citiestinyrefresh', verbosity=2,
		force_import_all=True, force_all=False,
		force_import=[], force=[])
	self.assertNotEqual(City.objects.get(
	    country__name_ascii='Russia', name_ascii='Moscow'), None)
	management.call_command('metrotinyimport', 'Russia', 'Moscow',
		os.path.join(os.path.dirname(__file__),
		    'data', 'RU', 'Moscow.ru.txt'))
	self.assertEqual(MetroLine.objects.count() >= 12, True)
	self.assertEqual(MetroStation.objects.count() >= 150, True)
