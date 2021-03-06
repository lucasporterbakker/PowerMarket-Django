from django.db import models

from powermarket.models import AbstractTimestampModel
from apps.user.models import Contact


class SupportAction(models.Model):
    """
    Allows the definition of support actions that have to be executed in a Support Ticket.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "%s" % self.name


class SupportTicket(AbstractTimestampModel):
    """
    Helps to manage a support request by keeping track of user details, response history, status, etc.
    """
    SUPPORT_STATUS_CHOICES = (
        ('requested', 'Support requested'),
        ('ongoing', 'Support ongoing'),
        ('hold', 'On hold'),
        ('done', 'Done'),
    )
    status = models.CharField(max_length=20, choices=SUPPORT_STATUS_CHOICES, default=SUPPORT_STATUS_CHOICES[0][0])
    assignee = models.CharField(max_length=255, null=True, blank=True)
    contact = models.ForeignKey(Contact, null=True, blank=True)
    required_actions = models.ManyToManyField(SupportAction, blank=True)
    zopim_user_id = models.CharField(max_length=255, null=True, blank=True)
    automatic = models.BooleanField(default=False)  # Whether the ticket was created by hand or by the system.

    def get_required_actions_list(self):
        return ", ".join([action.name for action in self.required_actions.all()])


class CallRequest(AbstractTimestampModel):
    """
    Generated by the request call form.
    """
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)
    contacted = models.BooleanField(default=False)


'''
class SupportRequest(AbstractTimestampModel):
    """
    Created by the Support Form.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
'''
