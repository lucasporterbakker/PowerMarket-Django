from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from apps.nrel.pvwatts5 import pvwatts5_request


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('lat', nargs=1, type=float)
        parser.add_argument('lon', nargs=1, type=float)
        parser.add_argument('area', nargs=1, type=float)

    def handle(self, *args, **options):
        point = Point(options['lat'][0], options['lon'][0])
        area = options['area'][0]
        response = pvwatts5_request(point, area)
        inputs = response.get('inputs')
        outputs = response.get('outputs')
        # errors = response.get('errors')
        # warnings = response.get('warnings')
        # version = response.get('version')
        station_info = response.get('station_info').get('distance') / 1000

        print(inputs)
        print(outputs)
        print(station_info)
