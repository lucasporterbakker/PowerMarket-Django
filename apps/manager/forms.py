from django import forms

from datetime import (
    date,
    datetime,
)

from powermarket.functions import dehumanize_decimal
from .models import (
    Project,
    ElectricityBill,
    Offer,
)


class ProjectForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    avg_monthly_consumption = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control humanize', 'placeholder': '0'}),
    )
    avg_monthly_bill = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control humanize', 'placeholder': '0'}),
    )

    class Meta:
        model = Project
        fields = (
            'avg_monthly_consumption',
            'avg_monthly_bill',
        )

    def clean_avg_monthly_consumption(self):
        return dehumanize_decimal(self.cleaned_data['avg_monthly_consumption'])

    def clean_avg_monthly_bill(self):
        return dehumanize_decimal(self.cleaned_data['avg_monthly_bill'])


class ElectricityBillForm(forms.ModelForm):

    month = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={
            'class': 'form-control text-center',
            'placeholder': 'MM',
            'required': 'required',
        }),
    )
    year = forms.IntegerField(
        required=True,
        min_value=(datetime.now().year - 2),
        max_value=datetime.now().year,
        widget=forms.NumberInput(attrs={
            'class': 'form-control text-center',
            'placeholder': 'YYYY',
            'required': 'required',
        }),
    )

    class Meta:
        model = ElectricityBill
        fields = (
            'project',
            'date',
            'month',
            'year',
            'private_file',
        )
        widgets = ({
            'project': forms.HiddenInput(),
            'date': forms.HiddenInput(),
        })

    def clean(self):
        cleaned_data = super(ElectricityBillForm, self).clean()
        month = cleaned_data['month']
        year = cleaned_data['year']
        if month and year:
            cleaned_data['date'] = date(
                year=year,
                month=month,
                day=1,
            )
        else:
            raise forms.ValidationError("Please enter a month and a year.")
        if cleaned_data['date'] > datetime.now().date():
            raise forms.ValidationError("Date can't be in the future.")
        project = cleaned_data['project']
        for bill in project.electricity_bills.all():
            if bill.date == cleaned_data['date']:
                raise forms.ValidationError("You already uploaded a bill for this month.")
        return cleaned_data


class OfferReviewForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('status',)
        widgets = ({
            'status': forms.HiddenInput(),
        })

    def clean(self):
        cleaned_data = super(OfferReviewForm, self).clean()
        btn = self.data['button']
        if btn == 'interested':
            cleaned_data['status'] = Offer.STATUS_INTERESTED
        elif btn == 'reject':
            cleaned_data['status'] = Offer.STATUS_REJECTED
        return cleaned_data
