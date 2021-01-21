from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from powermarket.email import send_templated_email
from apps.user.models import Contact
from .models import Assessment


# @receiver(post_save, sender=Contact)
# def contact_created(sender, instance, created, **kwargs):
#     if created:
#         assessment = get_object_or_404(Assessment, contact=instance)
#         print('contact created')
#         print(assessment)
#         email = send_templated_email(
#             subject='Assessment of your solar potential',
#             recipient_list=(instance.email,),
#             text_template='email/text/solar_potential_assessment.txt',
#             html_template='email/html/solar_potential_assessment.html',
#             context={
#                 'name': instance.name,
#                 'panel_area': assessment.panel_area,
#                 'annual_energy_production': assessment.annual_energy_production,
#                 'annual_savings_plus_earnings': assessment.annual_savings_plus_earnings,
#                 'unique_link': settings.SITE_URL + assessment.unique_link,
#             }
#         )
#         if email == 1:
#             assessment.email_sent = True
#             assessment.save()
