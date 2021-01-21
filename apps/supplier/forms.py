from django.contrib.gis import forms
from django.utils.translation import ugettext_lazy as _

from .models import SupplierContact


class SupplierContactForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    company = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Your company', 'class': 'input-lg'}),
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email address', 'class': 'input-lg'}),
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Phone number', 'class': 'input-lg'}),
        required=False
    )
    website = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'www.your-company.com', 'class': 'input-lg'}),
        required=False
    )
    type_of_business = forms.ChoiceField(
        label='',
        choices=SupplierContact.SUPPLIER_TYPE_CHOICES,
        widget=forms.RadioSelect(),
        help_text=_('Please select your type of business.')
    )

    class Meta:
        exclude = []
        model = SupplierContact
