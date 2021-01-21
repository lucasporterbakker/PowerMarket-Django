from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from powermarket.models import AbstractTimestampModel


class SupplierContact(AbstractTimestampModel):
    """
    Stores information from form on supplier info page.
    """
    SUPPLIER_TYPE_CHOICES = (
        ('system', _('Solar system supplier')),
        ('finance', _('Financing services')),
        ('maintenance', _('Maintenance contractor')),
        ('insurance', _('Insurance provider')),
        ('other', _('Other')),
    )
    company = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    website = models.CharField(max_length=50, null=True, blank=True)
    type_of_business = models.CharField(max_length=20, choices=SUPPLIER_TYPE_CHOICES)

    def __str__(self):
        return "%s" % self.company


class SupplierProfile(AbstractTimestampModel):
    """
    TBD..
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)

    def __str__(self):
        return "{}".format(self.name)
