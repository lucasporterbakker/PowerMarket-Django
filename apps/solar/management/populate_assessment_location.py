from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from apps.location.models import Location
from ..models import Assessment


class Command(BaseCommand):
    help = 'Populate assessment locations from polygon coordinates.'

    def handle(self, *args, **options):
        for assessment in Assessment.objects.all():
            if not assessment.location:
                print('Populating location for {}'.format(assessment.uuid))
                x, y = assessment.mpoly.centroid
                coords = Point(x, y)
                location = Location.objects.create(
                    address='Unknown',
                    coords=coords,
                )
                assessment.location = location
                assessment.save()


