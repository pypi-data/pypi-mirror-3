from django.core.management.base import BaseCommand, CommandError

from cities_tiny.models import Country, City
from metro_tiny.models import MetroLine, MetroStation

class Command(BaseCommand):
    args = '<Country name> <city name> <filename>'
    help = 'Imports metro stations and lines from a text file'

    def handle(self, *args, **options):
	try:
	    country_name, city_name, filename = args
	except ValueError:
	    raise CommandError("Invalid arguments")

	country = city = None

	try:
	    country = Country.objects.get(name_ascii=country_name)
	except Country.DoesNotExist:
	    pass
	if country is None:
	    try:
		country = Country.objects.get(name=country_name)
	    except Country.DoesNotExist:
		pass
	if country is None:
	    raise CommandError("Country not found: %s", country_name)

	try:
	    city = City.objects.get(country=country, name_ascii=city_name)
	except City.DoesNotExist:
	    pass
	if city is None:
	    try:
		city = City.objects.get(country=country, name=city_name)
	    except City.DoesNotExist:
		pass
	if city is None:
	    raise CommandError("City not found: %s", city_name)

	metro_line = None
	metro_line_count = metro_st_count = 0
	for line in open(filename).readlines():
	    ll = line.strip().decode('utf-8')
	    if not ll or ll.startswith('#'):
		continue
	    if ll.endswith(':'):
		name = ll.rstrip(':')
		metro_line, created = MetroLine.objects.get_or_create(
			city=city, name=name)
		if created:
		    metro_line_count += 1
	    elif metro_line is not None:
		name = ll
		metro_st, created = MetroStation.objects.get_or_create(
			line=metro_line, name=name)
		if created:
		    metro_st_count += 1

	print "Metro lines added: %d" % metro_line_count
	print "Metro stations added: %d" % metro_st_count
