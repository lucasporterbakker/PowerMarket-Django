from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, UpdateView

from powermarket.mixins import ModalResponseMixin
from .forms import *
from .models import ElectricityBill


class DashboardView(UpdateView):
    template_name = 'manager/dashboard.html'
    form_class = ProjectForm
    context_object_name = 'project'
    success_url = reverse_lazy('manager:dashboard')

    def get_object(self, queryset=None):
        return self.request.user.profile.selected_project

    def get_initial(self):
        initial = super(DashboardView, self).get_initial()
        avg_monthly_consumption = self.object.avg_monthly_consumption
        avg_monthly_bill = self.object.avg_monthly_bill
        if avg_monthly_consumption:
            initial['avg_monthly_consumption'] = intcomma(avg_monthly_consumption)
        if avg_monthly_bill:
            initial['avg_monthly_bill'] = intcomma(avg_monthly_bill)

        return initial


class ElectricityBillModalCreateView(
    ModalResponseMixin,
    CreateView,
):
    model = ElectricityBill
    form_class = ElectricityBillForm
    template_name = 'manager/modals/create_electricity_bill_modal.html'
    modal_title = _('Upload bill')
    project = None

    def dispatch(self, request, *args, **kwargs):
        self.project = self.request.user.profile.selected_project
        return super(ElectricityBillModalCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(ElectricityBillModalCreateView, self).get_initial()
        initial['project'] = self.project
        return initial

    def form_valid(self, form):
        response = super(ElectricityBillModalCreateView, self).form_valid(form)
        self.project.update_stage()
        return response


def delete_electricity_bill_view(request, pk):
    try:
        electricity_bill = ElectricityBill.objects.get(pk=pk)
        project = electricity_bill.project
        electricity_bill.delete()
        project.update_stage()
        messages.success(request, "Electricity bill successfully deleted.")
    except:
        messages.error(request, "There was an error, please try again.")
    return HttpResponseRedirect(reverse('manager:dashboard'))


class OfferReviewView(ModalResponseMixin, UpdateView):
    model = Offer
    form_class = OfferReviewForm
    template_name = 'manager/modals/review_offer_modal.html'


def pause_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.has_object_edit_permission(request):
        project.status = Project.STATUS_PAUSED
        project.save()
        return redirect(reverse('manager:dashboard'))
    else:
        return HttpResponseForbidden()


def resume_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.has_object_edit_permission(request):
        project.status = Project.STATUS_ACTIVE
        project.save()
        return redirect(reverse('manager:dashboard'))
    else:
        return HttpResponseForbidden()
