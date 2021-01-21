from django.contrib.gis import forms
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import SignupForm

from apps.user.models import Contact


class SelectAreaForm(forms.Form):
    mpoly = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    selected_area = forms.CharField(
        label='',
        widget=forms.HiddenInput(),
        required=False,
    )


class AssessmentSignupForm(SignupForm):
    required_css_class = 'required'
    error_css_class = 'error'

    assessment_uuid = forms.CharField(
        widget=forms.HiddenInput(),
    )
    email = forms.EmailField(
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Your email'),
                'class': 'input-lg',
            },
        ),
    )
    password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _('Choose password'),
                'class': 'input-lg',
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super(AssessmentSignupForm, self).__init__(*args, **kwargs)
        # The label attribute in the field definition
        # does not work, probably bc there is some magic
        # going on due to email/username options.
        self.fields['email'].label = ''


class ContactForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    assessment_uuid = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Contact
        fields = (
            'name',
            'email',
            'phone',
        )
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'eg. John Smith'}),
            'email': forms.EmailInput(attrs={'placeholder': 'eg. john@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': 'eg. 07123456789'}),
        }
