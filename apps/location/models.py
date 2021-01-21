from django.contrib.gis.db.models import PointField
from django.db import models

import uuid

from powermarket.models import AbstractTimestampModel


class Country(AbstractTimestampModel):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'countries'

    def __str__(self):
        return "{}".format(self.name)


class Locality(AbstractTimestampModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'localities'

    def __str__(self):
        return "{}".format(self.name)


class PostalCode(AbstractTimestampModel):
    code = models.CharField(max_length=20)

    def __str__(self):
        return "{}".format(self.code)


class Location(AbstractTimestampModel):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, null=True, blank=True)
    address = models.CharField(max_length=255)
    route = models.CharField(max_length=255, null=True, blank=True)
    street_number = models.CharField(max_length=10, null=True, blank=True)
    locality = models.ForeignKey(Locality, related_name='locations', null=True, blank=True, on_delete=models.SET_NULL)
    administrative_area_level_1 = models.CharField(max_length=255, null=True, blank=True)
    administrative_area_level_2 = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.ForeignKey(PostalCode, related_name='locations', null=True, blank=True)
    country = models.ForeignKey(Country, related_name='locations', null=True, blank=True, on_delete=models.SET_NULL)
    coords = PointField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.address)

    @property
    def lat(self):
        try:
            return self.coords.y
        except:
            pass

    @property
    def lng(self):
        try:
            return self.coords.x
        except:
            pass
