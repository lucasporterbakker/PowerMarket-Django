from django.conf import settings
from django.contrib.gis.geos import (
    GEOSGeometry,
    Point,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import (
    reverse,
    reverse_lazy,
)
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    FormView,
    TemplateView,
    UpdateView,
)

from allauth.account import app_settings as account_app_settings
from allauth.account.utils import complete_signup
from allauth.account.views import SignupView

from powermarket.choices import (
    CURRENCY_GBP,
    CURRENCY_INR,
)
from powermarket.email import send_templated_email
from powermarket.mixins import ModalResponseMixin
from apps.location.models import Location
from apps.manager.models import Project
from apps.nrel.pvwatts5 import pvwatts5_request
from apps.nrel.models import NoDataError
from apps.user.models import Contact
from .calculations import calc_monthly_profit
from .forms import (
    SelectAreaForm,
    AssessmentSignupForm,
    ContactForm,
)
from .models import (
    Assessment,
    ExampleAssessment,
)


class SelectAreaView(FormView):
    template_name = 'solar/select_area.html'
    form_class = SelectAreaForm
    address = settings.DEFAULT_ADDRESS
    location = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.location = Location.objects.get(uuid=self.kwargs.get('location_uuid'))
            if self.location.address:
                self.address = self.location.address
        except:
            pass
        return super(SelectAreaView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SelectAreaView, self).get_context_data(**kwargs)
        context['address'] = self.address
        return context

    def form_valid(self, form, **kwargs):
        mpoly = GEOSGeometry(form.cleaned_data['mpoly'])
        area = float(form.cleaned_data['selected_area'])
        # Until we add the ML estimation of tilt and azimuth, assume tilt=latitude and azimuth=180(Northern hemisphere) or 0 (S hemi)
        tilt=mpoly.centroid[0]
        if mpoly.centroid[0]>=0:
            azimuth=180
        else:
            azimuth=0

        location = self.location
        if location.country and location.country.name == 'India':
            nrel_results = pvwatts5_request(mpoly.centroid, area, tilt, azimuth, dataset='IN')
            inputs = nrel_results.get('inputs')
            outputs = nrel_results.get('outputs')
        else:
            nrel_results = pvwatts5_request(mpoly.centroid, area, tilt, azimuth)
            inputs = nrel_results.get('inputs')
            outputs = nrel_results.get('outputs')
            if not outputs:
                nrel_results = pvwatts5_request(mpoly.centroid, area, tilt, azimuth, dataset='tmy2')
                inputs = nrel_results.get('inputs')
                outputs = nrel_results.get('outputs')

        if not outputs: # handle no NREL data
            lat = float(inputs.get('lat'))
            lon = float(inputs.get('lon'))
            NoDataError.objects.create(location=Point(lon, lat))
            return HttpResponseRedirect(reverse('solar:no_data'))

        system_capacity_estimate = inputs.get('system_capacity')  # nameplate capacity in kW.
        ac_monthly = outputs.get('ac_monthly')
        ac_annual = outputs.get('ac_annual')

        country = 'United Kingdom'
        state = None
        currency = CURRENCY_GBP
        if location.country:
            if location.country.name == 'India':
                currency = CURRENCY_INR
                country = 'India'
                if location.administrative_area_level_1:
                    # TODO:
                    # Test and correct state names if necessary.
                    state = location.administrative_area_level_1

        monthly_savings, monthly_earnings = calc_monthly_profit(ac_monthly, country=country, state=state)

        assessment = Assessment(
            mpoly=mpoly,
            num_points=mpoly.num_points,
            location=location,
            selected_area=area,
            system_capacity_estimate=system_capacity_estimate,
            monthly_energy_estimates=ac_monthly,
            monthly_savings_estimates=monthly_savings,
            monthly_earnings_estimates=monthly_earnings,
            annual_energy_estimate=ac_annual,
            annual_savings_estimate=sum(monthly_savings),
            annual_earnings_estimate=sum(monthly_earnings),
            nrel_version=nrel_results.get('version'),
            nrel_station_distance=nrel_results.get('station_info').get('distance') / 1000,  # [km]
            currency=currency,
        )

        user = self.request.user
        if user.is_authenticated():
            Assessment.objects.filter(project__profile=user.profile).delete()
            assessment.project = user.profile.projects.first()

        assessment.save()

        send_templated_email(
            subject='PowerMarket Assessment Created',
            recipient_list=settings.MANAGERS,
            text_template='notification_email/assessment_created.txt',
            context={
                'short_link': 'https://' + get_current_site(self.request).domain + assessment.short_link,
            },
            fail_silently=True,
        )

        return HttpResponseRedirect(
            reverse(
                'solar:assessment',
                kwargs={'uuid': assessment.uuid},
            )
        )

class AssessmentOverlayView(CreateView):
    template_name = 'solar/assessment_overlay.html'
    form_class = ContactForm
    assessment = None

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, uuid=kwargs['uuid'])
        if (self.assessment.contact or self.assessment.project
                or request.user.is_staff or self.assessment.supervised):
            return HttpResponseRedirect(
                reverse(
                    'solar:assessment',
                    kwargs={'uuid': self.assessment.uuid},
                )
            )
        return super(AssessmentOverlayView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssessmentOverlayView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context

    def get_initial(self):
        initial = super(AssessmentOverlayView, self).get_initial()
        initial['assessment_uuid'] = self.assessment
        return initial

    def form_valid(self, form):
        contact = form.save()
        self.assessment = get_object_or_404(Assessment, uuid=form.cleaned_data['assessment_uuid'])
        self.assessment.contact = contact

        short_link = 'https://' + get_current_site(self.request).domain + self.assessment.short_link

        email = send_templated_email(
            subject='Your PowerMarket Solar Report',
            recipient_list=(contact.email,),
            text_template='email/text/solar_potential_assessment.txt',
            html_template='email/html/solar_potential_assessment.html',
            context={
                'name': contact.name,
                'assessment': self.assessment,
            },
            fail_silently=True,
        )
        if email == 1:
            self.assessment.email_sent = True

        self.assessment.save()

        send_templated_email(
            subject='PowerMarket contact created',
            recipient_list=settings.MANAGERS,
            text_template='notification_email/contact_created.txt',
            context={
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'short_link': short_link,
            },
            fail_silently=True,
        )

        return HttpResponseRedirect(reverse('solar:assessment', kwargs={'uuid': self.assessment.uuid}))


def connect_linkedin_view(request, uuid):
    user = request.user
    profile = user.profile

    socialaccount = user.socialaccount_set.first()

    profile.first_name = socialaccount.extra_data.get('firstName')
    profile.last_name = socialaccount.extra_data.get('lastName')
    profile.linkedin_url = socialaccount.extra_data.get('publicProfileUrl')
    profile.save()

    project = Project.objects.get(profile=user.profile)
    assessment = Assessment.objects.get(uuid=uuid)
    assessment.project = project

    short_link = 'http://' + get_current_site(request).domain + assessment.short_link

    name = "{first_name} {last_name}".format(
        first_name=profile.first_name,
        last_name=profile.last_name,
    )

    email = socialaccount.extra_data.get('emailAddress')

    email_status = send_templated_email(
        subject='Your PowerMarket Solar Report',
        recipient_list=(user.email,),
        text_template='email/text/solar_potential_assessment.txt',
        html_template='email/html/solar_potential_assessment.html',
        context={
            'name': name,
            'assessment': assessment,
        },
        fail_silently=True,
    )
    if email_status == 1:
        assessment.email_sent = True

    assessment.save()

    project.update_stage()
    project.save()

    send_templated_email(
        subject='PowerMarket LinkedIn contact created',
        recipient_list=settings.MANAGERS,
        text_template='notification_email/contact_created.txt',
        context={
            'name': name,
            'email': email,
            'short_link': short_link,
        },
        fail_silently=True,
    )

    return HttpResponseRedirect(reverse('solar:assessment', kwargs={'uuid': assessment.uuid}))


'''
class AssessmentView(TemplateView):
    template_name = 'solar/assessment.html'
    assessment = None

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, uuid=kwargs['uuid'])
        if (not self.assessment.contact and not self.assessment.project
                and not request.user.is_staff and not self.assessment.supervised):
            return HttpResponseRedirect(
                reverse(
                    'solar:assessment_overlay',
                    kwargs={'uuid': self.assessment.uuid},
                )
            )
        return super(AssessmentView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssessmentView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context
'''


class AssessmentView(SignupView):
    template_name = 'solar/assessment.html'
    form_class = AssessmentSignupForm
    assessment = None

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, uuid=kwargs['uuid'])
        if (not self.assessment.contact and not self.assessment.project
                and not request.user.is_staff and not self.assessment.supervised):
            return HttpResponseRedirect(
                reverse(
                    'solar:assessment_overlay',
                    kwargs={'uuid': self.assessment.uuid},
                )
            )
        return super(FormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssessmentView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['contact_form'] = ContactForm(initial={'assessment_uuid': self.assessment.uuid})
        # context['signup'] = True
        return context

    def get_initial(self):
        initial = super(AssessmentView, self).get_initial()
        initial['assessment_uuid'] = self.assessment.uuid
        if self.assessment.contact:
            initial['email'] = self.assessment.contact.email
        return initial

    def form_valid(self, form):
        form_valid_response = super(AssessmentView, self).form_valid(form)
        if self.user:
            assessment = Assessment.objects.get(uuid=form.cleaned_data['assessment_uuid'])
            assessment.project = self.user.profile.projects.first()
            assessment.save()
            assessment.project.status = Project.STATUS_ACTIVE
            assessment.project.stage = Project.STAGE_DATA_COLLECTION
            assessment.project.save()

            # Notify managers.
            send_templated_email(
                subject='PowerMarket User Signup',
                recipient_list=settings.MANAGERS,
                text_template='notification_email/user_signup.txt',
                context={
                    'short_link': 'http://' + get_current_site(self.request).domain + assessment.short_link,
                },
                fail_silently=True,
            )
        return form_valid_response

class AssessmentViewML(SignupView):
    template_name = 'solar/assessmentml.html'
    form_class = AssessmentSignupForm
    assessment = None

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, uuid=kwargs['uuid'])
        if (not self.assessment.contact and not self.assessment.project
                and not request.user.is_staff and not self.assessment.supervised):
            return HttpResponseRedirect(
                reverse(
                    'solar:assessment_overlay',
                    kwargs={'uuid': self.assessment.uuid},
                )
            )
        return super(FormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssessmentViewML, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['contact_form'] = ContactForm(initial={'assessment_uuid': self.assessment.uuid})
        # context['signup'] = True
        return context

    def get_initial(self):
        initial = super(AssessmentViewML, self).get_initial()
        initial['assessment_uuid'] = self.assessment.uuid
        if self.assessment.contact:
            initial['email'] = self.assessment.contact.email
        return initial

    def form_valid(self, form):
        form_valid_response = super(AssessmentViewML, self).form_valid(form)
        if self.user:
            assessment = Assessment.objects.get(uuid=form.cleaned_data['assessment_uuid'])
            assessment.project = self.user.profile.projects.first()
            assessment.save()
            assessment.project.status = Project.STATUS_ACTIVE
            assessment.project.stage = Project.STAGE_DATA_COLLECTION
            assessment.project.save()

            # Notify managers.
            send_templated_email(
                subject='PowerMarket User Signup',
                recipient_list=settings.MANAGERS,
                text_template='notification_email/user_signup.txt',
                context={
                    'short_link': 'http://' + get_current_site(self.request).domain + assessment.short_link,
                },
                fail_silently=True,
            )
        return form_valid_response


class SharedAssessmentView(AssessmentView):
    def get_context_data(self, **kwargs):
        ctx = super(SharedAssessmentView, self).get_context_data(**kwargs)
        ctx['shared'] = True
        return ctx


class AssessmentSignupModalView(
    ModalResponseMixin,
    FormView,
):
    form_class = AssessmentSignupForm
    template_name = 'solar/modals/assessment_signup_modal.html'
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Assessment, uuid=kwargs['uuid'])
        return super(FormView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(AssessmentSignupModalView, self).get_initial()
        initial['assessment_uuid'] = self.object.uuid
        return initial

    def get_success_url(self):
        return reverse('manager:dashboard')

    def form_valid(self, form):
        user = form.save(self.request)
        try:
            complete_signup(
                self.request, user,
                account_app_settings.EMAIL_VERIFICATION,
                self.get_success_url(),
            )
            assessment = self.object
            assessment.project = user.profile.projects.first()
            assessment.save()
            assessment.project.status = Project.STATUS_ACTIVE
            assessment.project.stage = Project.STAGE_DATA_COLLECTION
            assessment.project.save()
            send_templated_email(
                subject='PowerMarket User Signup',
                recipient_list=settings.MANAGERS,
                text_template='notification_email/user_signup.txt',
                context={
                    'short_link': 'http://' + get_current_site(self.request).domain + assessment.short_link,
                },
                fail_silently=True,
            )
            return self.render_to_response(_, valid=True)
        except:
            return Http404()


class AssessmentNotesUpdateView(ModalResponseMixin, UpdateView):
    model = Assessment
    fields = ('notes',)


class SendReportView(CreateView):
    model = Contact
    form_class = ContactForm
    assessment = None

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, uuid=self.kwargs['uuid'])
        return super(SendReportView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super(SendReportView, self).form_valid(form)
        contact = self.object
        assessment = self.assessment
        assessment.contact = contact
        current_site = get_current_site(self.request)
        email = send_templated_email(
            subject='Assessment of your solar potential',
            recipient_list=(contact.email,),
            text_template='email/text/solar_potential_assessment.txt',
            html_template='email/html/solar_potential_assessment.html',
            context={
                'name': contact.name,
                'assessment': assessment,
                'short_link': 'https://' + current_site.domain + assessment.short_link,
            },
            fail_silently=False,
        )
        if email == 1:
            assessment.email_sent = True
        assessment.save()
        send_templated_email(
            subject='PowerMarket Contact Created',
            recipient_list=settings.MANAGERS,
            text_template='notification_email/contact_created.txt',
            context={
                'name': contact.name,
                'email': contact.email,
                'short_link': settings.HTTP_PROTOCOL + '://' + get_current_site(self.request).domain + assessment.short_link,
            },
            fail_silently=True,
        )
        return response

    def get_success_url(self):
        return reverse('solar:assessment', kwargs={'uuid': self.assessment.uuid})


class ExampleAssessmentView(TemplateView):
    template_name = 'solar/assessment.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super(ExampleAssessmentView, self).get_context_data(**kwargs)
        if slug:
            example = get_object_or_404(ExampleAssessment, slug=slug, published=True)
        else:
            example = ExampleAssessment.objects.first()
        context.update({
            'assessment': example.assessment,
            'name': example.name,
            'address': example.address,
            'info': example.info,
            'example': True,
        })
        return context


def report_link_view(request, **kwargs):
    return redirect(reverse('solar:assessment', kwargs={'uuid': kwargs['uuid']}))


class RequestOfferView(ModalResponseMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'modal.html'
    success_url = reverse_lazy('solar:thank_you')
    modal_title = _('Request an offer')
    modal_content = _('Fill the form below and we\'ll get in contact with different suppliers to find '
                      'the best offer for your project. This service is entirely free for you!')
    form_submit_label = _('Send me an offer')
    assessment = None

    def get_context_data(self, **kwargs):
        context = super(RequestOfferView, self).get_context_data(**kwargs)
        self.assessment = get_object_or_404(Assessment, uuid=self.kwargs['uuid'])
        context['assessment'] = self.assessment
        return context

    def get_initial(self):
        initial = super(RequestOfferView, self).get_initial()
        initial['assessment_uuid'] = self.assessment
        return initial

    def get_form_info(self):
        terms_url = reverse_lazy('terms_of_service')
        return 'By clicking \'Send me an offer\' you agree to our <a href="{}">Terms of Service</a>.'.format(terms_url)

    def form_valid(self, form):
        contact = form.save()
        self.assessment = get_object_or_404(Assessment, uuid=form.cleaned_data['assessment_uuid'])
        self.assessment.contact = contact
        current_site = get_current_site(self.request)
        email = send_templated_email(
            subject='Assessment of your solar potential',
            recipient_list=(contact.email,),
            text_template='email/text/solar_potential_assessment.txt',
            html_template='email/html/solar_potential_assessment.html',
            context={
                'name': contact.name,
                'assessment': self.assessment,
                'short_link': 'http://' + current_site.domain + self.assessment.short_link,
            },
            fail_silently=True,
        )
        if email == 1:
            self.assessment.email_sent = True

        self.assessment.save()

        send_templated_email(
            subject='PowerMarket Offer Request',
            recipient_list=settings.MANAGERS,
            text_template='notification_email/offer_request_created.txt',
            context={
                'name': contact.name,
                'email': contact.email,
                'company': contact.company,
                'phone': contact.phone,
                'short_link': 'http://' + current_site.domain + self.assessment.short_link,
            },
            fail_silently=True,
        )

        return self.render_to_response(form, valid=True)


# Static views.
# -----------------------------------------------------------------------------

class NoDataView(TemplateView):
    template_name = 'solar/no_data.html'


class ThankYouView(TemplateView):
    template_name = 'solar/thank_you.html'

