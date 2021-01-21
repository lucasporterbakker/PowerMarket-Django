from django.db import models


class AbstractTimestampModel(models.Model):
    """
    Extends default django model with created
    and modified timestamps.
    """
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
