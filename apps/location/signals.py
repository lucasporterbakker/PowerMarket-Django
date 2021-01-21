from django.db.models.signals import pre_save
from django.dispatch import receiver

import itertools

from .functions import slug_from_address
from .models import Location


# @receiver(pre_save, sender=Location)
# def check_location_slug(sender, instance, **kwargs):
#     if not instance.slug:
#         instance.slug = slug_from_address(instance.address)
#     original_slug = instance.slug
#     for i in itertools.count(2):
#         qs = Location.objects.filter(slug=instance.slug)
#         if instance.pk:
#             # Exclude self if instance already exists in DB.
#             qs = qs.exclude(pk=instance.pk)
#         if not qs.exists():
#             break
#         instance.slug = '{0:s}-{1:d}'.format(original_slug, i)
