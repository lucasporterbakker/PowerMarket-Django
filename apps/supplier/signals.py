from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from powermarket.email import send_templated_email
from .models import SupplierContact


@receiver(post_save, sender=SupplierContact)
def supplier_contact_created(sender, instance, created, **kwargs):
    if created:
        send_templated_email(
            subject='PowerMarket Supplier Contact',
            recipient_list=settings.MANAGERS,
            text_template='email/text/supplier_contact_created.txt',
            context={
                'company': instance.company,
                'email': instance.email,
                'phone': instance.phone,
                'website': instance.website,
                'type_of_business': instance.get_type_of_business_display(),
            }
        )
