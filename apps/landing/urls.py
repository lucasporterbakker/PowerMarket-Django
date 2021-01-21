from django.conf.urls import url

from .views import *


urlpatterns = [

    # Landing page.
    url(r'^$', LandingPageView.as_view(), name='landing_page'),

    # About.
    url(r'^company/$', CompanyPageView.as_view(), name='company'),
    url(r'^work-with-us/$', WorkWithUsPageView.as_view(), name='work_with_us'),
    url(r'^technology/$', TechnologyPageView.as_view(), name='technology'),
    url(r'^investors/$', InvestorPageView.as_view(), name='investors'),
    url(r'^press/$', PressPageView.as_view(), name='press'),
    url(r'^blog/amp/(?P<slug>[\w-]+)/$', BlogArticleAMPView.as_view(), name='blog_amp'),
    url(r'^blog/(?P<slug>[\w-]+)/$', BlogArticlePageView.as_view(), name='blog'),
    url(r'^blog/$', BlogPageView.as_view(), name='blog'),
    url(r'^faq/$', FAQPageView.as_view(), name='faq'),

    # Solar.
    url(r'^commercial-solar/$', CommercialSolarView.as_view(), name='commercial_solar'),
    url(r'^financing-commercial-solar-projects/$', FinancingView.as_view(), name='financing'),
    url(r'^government-incentives/$', SolarIncentivesView.as_view(), name='incentives'),
    url(r'^solar-101/$', LexiconView.as_view(), name='solar_101'),

    # Markets.
    url(r'^markets/(?P<country>[a-zA-Z_.-]*)/$', SolarMarketView.as_view(), name='markets'),

    # Legal.
    url(r'^terms-of-service/$', TermsOfServiceView.as_view(), name='terms_of_service'),
    url(r'^privacy-policy/$', PrivacyPolicyView.as_view(), name='privacy_policy'),
    url(r'^cookie-use/$', CookiePolicyView.as_view(), name='cookie_use'),
    url(r'^attribution/$', AttributionView.as_view(), name='attribution'),
]
