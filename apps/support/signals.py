from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from powermarket.email import send_templated_email
from .models import CallRequest


@receiver(post_save, sender=CallRequest)
def call_requested(sender, instance, created, **kwargs):
    if created:
        send_templated_email(
            subject='PowerMarket Call Request',
            recipient_list=settings.MANAGERS,
            text_template='email/text/call_requested.txt',
            context={
                'name': instance.name,
                'phone': instance.phone,
                'note': instance.note
            }
        )
