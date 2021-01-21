from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from powermarket.models import AbstractTimestampModel


class Contact(AbstractTimestampModel):
    """
    Stores user information for the case that
    the user did not register.
    """
    STATUS_CONTACT_CREATED = 0
    STATUS_CONTACTED = 1
    STATUS_PROCESSING = 2
    STATUS_OFFER_DELIVERED = 3
    STATUS_SALE_COMPLETE = 4
    STATUS_NO_RESPONSE = 5
    STATUS_NOT_INTERESTED = 6
    STATUS_FAKE = 7
    STATUS_CHOICES = (
        (STATUS_CONTACT_CREATED, 'contact created'),
        (STATUS_CONTACTED, 'contacted by team'),
        (STATUS_PROCESSING, 'offer processing'),
        (STATUS_OFFER_DELIVERED, 'offer delivered'),
        (STATUS_SALE_COMPLETE, 'sale complete'),
        (STATUS_NO_RESPONSE, 'no response'),
        (STATUS_NOT_INTERESTED, 'not interested'),
        (STATUS_FAKE, 'fake contact'),
    )

    name = models.CharField(_('first and last name'), max_length=255)
    email = models.EmailField(_('Email address'))
    company = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(_('phone number'), max_length=255, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    status_modified_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    test = models.BooleanField(_('test contact'), default=False)
    qualified_lead = models.BooleanField(_('qualified lead'), default=False)
    fake = models.BooleanField(_('fake'), default=False)

    def __str__(self):
        return "{}".format(self.email)


class ContactNote(AbstractTimestampModel):
    """
    Notes created by staff regarding
    contact interaction and sales cycle.
    """
    contact = models.ForeignKey(
        Contact,
        related_name='notes',
        null=True, blank=True,
    )
    note = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_contact_notes',
        null=True, blank=True,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='modified_contact_notes',
        null=True, blank=True,
    )

    def __str__(self):
        return "{}".format(self.note)


class StaffProfile(AbstractTimestampModel):
    """
    Extends standard User model for staff members
    to improve customer interaction and workflow.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='staff_profile')

    def __str__(self):
        return "{}".format(self.user.username)


class UserProfile(AbstractTimestampModel):
    """
    Extends standard User model to hold all
    user specific information.
    """
    STATUS_PROFILE_CREATED = 0
    STATUS_CHOICES = (
        (STATUS_PROFILE_CREATED, 'profile created'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='profile')
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    linkedin_url = models.URLField(null=True, blank=True)

    test = models.BooleanField(default=False)
    qualified_lead = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('user profile')

    def __str__(self):
        return "{}".format(self.user.username)

    # Permissions.
    # ---------------------------

    def has_object_edit_permission(self, request):
        if request.user.is_authenticated():
            return request.user.profile == self

    @property
    def email(self):
        return "{}".format(self.user.email)

    @property
    def information_complete(self):
        return self.first_name and self.last_name and self.company and self.phone

    @property
    def selected_project(self):
        return self.projects.first()


class ProfileNote(AbstractTimestampModel):
    """
    Notes created by staff regarding
    profile interaction and sales cycle.
    """
    profile = models.ForeignKey(
        UserProfile,
        related_name='notes',
        null=True, blank=True,
    )
    note = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_profile_notes',
        null=True, blank=True,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='modified_profile_notes',
        null=True, blank=True,
    )

    def __str__(self):
        return "{}".format(self.note)
