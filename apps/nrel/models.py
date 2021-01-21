from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from powermarket.models import AbstractTimestampModel


class NoDataError(AbstractTimestampModel):
    location = models.PointField(_('geo location [deg]'), null=True, blank=True)
    used_search_radius = models.FloatField(_('used search radius [km]'), null=True, blank=True)

    def __str__(self):
        return "{date} ({lat}, {lon})".format(
            date=self.created.date(),
            lat=self.location.coords[0],
            lon=self.location.coords[1],
        )

    @property
    def lat(self):
        return self.location.y

    @property
    def lon(self):
        return self.location.x
