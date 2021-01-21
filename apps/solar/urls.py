from django.conf.urls import url

from . import views


urlpatterns = [

    url(r'^request-offer/(?P<uuid>[\w-]+)/$',
        views.RequestOfferView.as_view(),
        name='request_offer',
        ),
    url(r'^assessment/(?P<pk>[0-9]+)/notes/update/$',
        views.AssessmentNotesUpdateView.as_view(),
        name='assessment_notes_update',
        ),

    url(r'^area/$', views.SelectAreaView.as_view(), name='area'),
    url(r'^area/(?P<location_uuid>[\w-]+)/$', views.SelectAreaView.as_view(), name='area'),
    url(r'^no-data/$', views.NoDataView.as_view(), name='no_data'),
    url(r'^assessment/example/(?P<slug>[\w-]+)/$', views.ExampleAssessmentView.as_view(), name='example_assessment'),
    url(r'^assessment/example/$', views.ExampleAssessmentView.as_view(), name='example_assessment'),
    url(r'^assessment/(?P<uuid>[\w-]+)/connect-linkedin/$', views.connect_linkedin_view, name='connect_linkedin'),
    url(r'^assessment/(?P<uuid>[\w-]+)/signup/$', views.AssessmentSignupModalView.as_view(), name='assessment_signup_modal'),
    url(r'^assessment/(?P<uuid>[\w-]+)/shared/$', views.SharedAssessmentView.as_view(), name='shared_assessment'),
    url(r'^assessment/(?P<uuid>[\w-]+)/overlay/$', views.AssessmentOverlayView.as_view(), name='assessment_overlay'),
    url(r'^assessment/(?P<uuid>[\w-]+)/$', views.AssessmentView.as_view(), name='assessment'),
    url(r'^assessmentml/(?P<uuid>[\w-]+)/$', views.AssessmentViewML.as_view(), name='assessmentml'),
    url(r'^send-report/(?P<uuid>[\w-]+)/$', views.SendReportView.as_view(), name='send_report'),
    url(r'^thank-you/$', views.ThankYouView.as_view(), name='thank_you'),
]
