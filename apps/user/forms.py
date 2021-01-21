from django import forms

from .models import *


class PersonalInformationForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'company',
            'phone',
        )
