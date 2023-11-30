# myapp/forms.py
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Address
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'phone_number']

    


class AddressForm(forms.ModelForm):

    country = CountryField().formfield()
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code', 'country']
        
