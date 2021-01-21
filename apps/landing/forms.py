from django import forms
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _

from apps.location.models import (
    Country,
    Locality,
    Location,
    PostalCode,
)


class AddressForm(forms.Form):

    address = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Enter your address or postcode'),
                'class': 'form-control input-lg',
                'required': 'required',
            }
        )
    )

    uuid = forms.CharField(required=False, widget=forms.HiddenInput())

    route = forms.CharField(required=False, widget=forms.HiddenInput())
    street_number = forms.CharField(required=False, widget=forms.HiddenInput())
    locality = forms.CharField(required=False, widget=forms.HiddenInput())
    administrative_area_level_1 = forms.CharField(required=False, widget=forms.HiddenInput())
    administrative_area_level_2 = forms.CharField(required=False, widget=forms.HiddenInput())
    postal_code = forms.CharField(required=False, widget=forms.HiddenInput())
    country = forms.CharField(required=False, widget=forms.HiddenInput())
    lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    lng = forms.FloatField(required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(AddressForm, self).clean()
        address = cleaned_data['address']

        if address:
            locality = None
            postal_code = None
            country = None
            coords = None
            if cleaned_data.get('locality'):
                locality, created = Locality.objects.get_or_create(name=cleaned_data['locality'])
            if cleaned_data.get('postal_code'):
                postal_code, created = PostalCode.objects.get_or_create(code=cleaned_data['postal_code'])
            if cleaned_data.get('country'):
                country, created = Country.objects.get_or_create(name=cleaned_data['country'])
            if cleaned_data.get('lat') and cleaned_data.get('lng'):
                coords = Point(cleaned_data['lng'], cleaned_data['lat'])
            location = Location.objects.create(
                address=address,
                route=cleaned_data['route'],
                street_number=cleaned_data['street_number'],
                locality=locality,
                administrative_area_level_1=cleaned_data['administrative_area_level_1'],
                administrative_area_level_2=cleaned_data['administrative_area_level_2'],
                postal_code=postal_code,
                country=country,
                coords=coords,
            )
            cleaned_data['uuid'] = location.uuid

        return cleaned_data
