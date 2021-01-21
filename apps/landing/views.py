from django.template import loader as template_loader, TemplateDoesNotExist
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, ListView

from apps.solar.models import ExampleAssessment
from .forms import AddressForm
from .models import *


class LandingPageView(FormView):
    template_name = 'landing/landing_page.html'
    form_class = AddressForm

    def get_context_data(self, **kwargs):
        context = super(LandingPageView, self).get_context_data(**kwargs)
        examples = ExampleAssessment.objects.all().order_by('assessment__annual_energy_estimate')
        context.update({'examples': examples})
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            # Redirect if user is logged in.
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(LandingPageView, self).get(self, request, args, **kwargs)

    def form_valid(self, form):
        uuid = form.cleaned_data['uuid']
        return HttpResponseRedirect(reverse('solar:area', kwargs={'location_uuid': uuid}))


# -----------------------------------------------------------------------------
# About pages.
# -----------------------------------------------------------------------------

class CompanyPageView(TemplateView):
    template_name = 'landing/about/company.html'


class WorkWithUsPageView(TemplateView):
    template_name = 'landing/about/work_with_us.html'


class InvestorPageView(TemplateView):
    template_name = 'landing/about/investors.html'


class TechnologyPageView(TemplateView):
    template_name = 'landing/about/technology.html'


class PressPageView(ListView):
    model = PressEntry
    template_name = 'landing/about/press.html'


class FAQPageView(TemplateView):
    template_name = 'landing/about/faq.html'


class BlogPageView(TemplateView):
    template_name = 'landing/about/blog.html'


class BlogArticlePageView(TemplateView):
    template_file_name = None
    slug = None

    def dispatch(self, request, *args, **kwargs):
        self.slug = self.kwargs.get('slug')
        self.template_file_name = self.slug.replace('-', '_') + ".html"
        return super(BlogArticlePageView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return 'landing/blog/' + self.template_file_name

    def get_context_data(self, **kwargs):
        ctx = super(BlogArticlePageView, self).get_context_data(**kwargs)
        amp_template_name = 'landing/blog/amp/' + self.template_file_name
        try:
            amp_template = template_loader.get_template(amp_template_name)
        except TemplateDoesNotExist:
            amp_template = None
        ctx['has_amp_page'] = amp_template is not None
        ctx['slug'] = self.slug
        return ctx


class BlogArticleAMPView(TemplateView):
    def get_template_names(self):
        return 'landing/blog/amp/' + self.kwargs.get('slug').replace('-', '_') + ".html"


# -----------------------------------------------------------------------------
# Solar pages.
# -----------------------------------------------------------------------------

class CommercialSolarView(TemplateView):
    template_name = 'landing/solar/commercial_solar.html'


class SolarIncentivesView(TemplateView):
    template_name = 'landing/solar/incentives.html'


class FinancingView(TemplateView):
    template_name = 'landing/solar/financing.html'


class LexiconView(ListView):
    template_name = 'landing/solar/lexicon.html'
    model = LexiconEntry
    queryset = LexiconEntry.objects.filter(published=True).order_by('term')


# -----------------------------------------------------------------------------
# Market pages.
# -----------------------------------------------------------------------------

class SolarMarketView(TemplateView):
    """
    Dynamically handles handles all Markets templates with a single view.
    Returns country specific template, 'under construction' template or 404 depending on kwarg parameter.
    """
    available_countries = ['uk', 'united_states', 'china', 'germany']

    def get_template_names(self):
        country = self.kwargs.get('country')
        if country in self.available_countries:
            return 'landing/markets/' + country + '.html'
        elif country in ['france', 'japan', 'india', 'australia']:
            # Upcoming markets.
            return 'landing/markets/under_construction.html'
        else:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super(SolarMarketView, self).get_context_data(**kwargs)
        context['country'] = self.kwargs.get('country').title()
        return context


# -----------------------------------------------------------------------------
# Legal pages.
# -----------------------------------------------------------------------------

class TermsOfServiceView(TemplateView):
    template_name = 'landing/legal/terms_of_service.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'landing/legal/privacy_policy.html'


class CookiePolicyView(TemplateView):
    template_name = 'landing/legal/cookie_use.html'


class AttributionView(TemplateView):
    template_name = 'landing/legal/attribution.html'
