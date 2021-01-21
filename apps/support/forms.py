from django import forms

from .models import CallRequest


class CallRequestForm(forms.ModelForm):
    name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Your name', 'class': 'input-lg'}),
    )
    phone = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Your phone number', 'class': 'input-lg'}),
    )
    note = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'placeholder': 'Add a note...', 'class': 'input-lg'}),
    )

    class Meta:
        model = CallRequest
        exclude = ['contacted']
