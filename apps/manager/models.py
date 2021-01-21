from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from private_storage.fields import PrivateFileField
from private_storage.permissions import *

from powermarket.models import AbstractTimestampModel
from powermarket.choices import (
    CURRENCY_CHOICES,
    CURRENCY_GBP,
)
from apps.user.models import UserProfile
from apps.supplier.models import SupplierProfile


class Project(AbstractTimestampModel):
    STATUS_ACTIVE = 0
    STATUS_PAUSED = 1
    STATUS_COMPLETE = 2
    STATUS_CHOICES = (
        (STATUS_ACTIVE, _('active')),
        (STATUS_PAUSED, _('paused')),
        (STATUS_COMPLETE, _('complete')),
    )
    STAGE_ASSESSMENT = 0
    STAGE_DATA_COLLECTION = 1
    STAGE_PROJECT_DESIGN = 2
    STAGE_PERMISSIONS = 3
    STAGE_KICKOFF = 4
    STAGE_CHOICES = (
        (STAGE_ASSESSMENT, _('solar assessment')),
        (STAGE_DATA_COLLECTION, _('data collection')),
        (STAGE_PROJECT_DESIGN, _('project design')),
        (STAGE_PERMISSIONS, _('permissions & approvals')),
        (STAGE_KICKOFF, _('project kick-off'))
    )

    profile = models.ForeignKey(UserProfile, null=True, blank=True, related_name='projects')
    name = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    stage = models.IntegerField(choices=STAGE_CHOICES, default=STAGE_ASSESSMENT)

    avg_monthly_consumption = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)  # [kWh]
    avg_monthly_bill = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)  # [GBP]

    def __str__(self):
        return "{}".format(self.project_id)

    # Permissions.
    # ---------------------------

    def has_object_edit_permission(self, request):
        if request.user.is_authenticated():
            return request.user.profile == self.profile

    # END permissions.

    @property
    def project_id(self):
        return "PM / S {}-{:04d}".format(self.created.strftime('%Y%m%d'), self.id)

    @property
    def selected_assessment(self):
        return self.assessments.order_by('-created').first()

    @property
    def country(self):
        assessment = self.selected_assessment
        if assessment:
            return assessment.country

    @property
    def currency(self):
        assessment = self.selected_assessment
        if assessment:
            return assessment.currency

    @property
    def data_complete(self):
        return self.avg_monthly_consumption and self.avg_monthly_bill

    def update_stage(self):
        if not self.selected_assessment:
            self.stage = self.STAGE_ASSESSMENT
        else:
            if not (self.profile.information_complete and self.data_complete and
                    self.electricity_bills.count() >= settings.REQUIRED_ELECTRICITY_BILLS):
                self.stage = self.STAGE_DATA_COLLECTION
            else:
                self.stage = self.STAGE_PROJECT_DESIGN
        self.save()


class Offer(AbstractTimestampModel):
    STATUS_CREATED = 0
    STATUS_REJECTED = 1
    STATUS_INTERESTED = 2
    STATUS_PROCESSING = 3
    STATUS_SUCCESSFUL = 4
    STATUS_UNSUCCESSFUL = 5
    STATUS_CHOICES = (
        (STATUS_CREATED, _('waiting for review')),
        (STATUS_REJECTED, _('rejected')),
        (STATUS_INTERESTED, _('interested')),
        (STATUS_PROCESSING, _('processing')),
        (STATUS_SUCCESSFUL, _('successful')),
        (STATUS_UNSUCCESSFUL, _('unsuccessful')),
    )

    project = models.ForeignKey(Project, related_name='offers', verbose_name=_('project'), null=True)
    supplier = models.ForeignKey(SupplierProfile, related_name='offers')
    headline = models.CharField(max_length=50)
    message = models.TextField()
    attachment = models.FileField(upload_to='uploads/offer_attachments/', null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    @property
    def age_in_days(self):
        return (timezone.now() - self.created).days


class ElectricityBill(AbstractTimestampModel):
    project = models.ForeignKey(Project, related_name='electricity_bills', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    private_file = PrivateFileField(
        upload_to='uploads/electricity_bills/',
        help_text='Please upload a .pdf file if possible.',
        null=True,
    )

    def __str__(self):
        return "Electricity bill - {}".format(self.date_str)

    @property
    def date_str(self):
        if self.date:
            date_str = self.date.strftime("%b. %Y")
        else:
            date_str = "unknown"
        return "{}".format(date_str)
