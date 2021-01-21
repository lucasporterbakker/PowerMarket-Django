from django.conf.urls import url

from .views import *


urlpatterns = [

    # AJAX views.
    url(r'^profile/(?P<pk>[0-9]+)/personal-information/update/$', PersonalInformationUpdateView.as_view(),
        name='personal_information_update'),
    url(r'^profile/(?P<pk>[0-9]+)/delete-account/$', DeleteAccountView.as_view(), name='delete_account'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),

    # Admin views.
    url(r'^contact-note/create/$',
        ContactNoteCreateView.as_view(),
        name='contact_note_create',
        )
]
