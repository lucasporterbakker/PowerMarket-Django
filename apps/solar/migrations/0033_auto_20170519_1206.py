# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-05-19 12:06
from __future__ import unicode_literals

from django.contrib.gis.geos import Point
from django.db import migrations

from apps.location.models import Location
from ..models import Assessment


def populate_assessment_location(apps, schema_editor):
    for assessment in Assessment.objects.all():
        if not assessment.location:
            try:
                x, y = assessment.mpoly.centroid
                coords = Point(x, y)
                location = Location.objects.create(
                    address='Unknown',
                    coords=coords,
                )
                assessment.location = location
                assessment.save()
            except:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0032_auto_20170518_2014'),
    ]

    operations = [
        migrations.RunPython(populate_assessment_location),
    ]