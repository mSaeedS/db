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
        
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize the form's appearance here, e.g., placeholders, labels, etc.
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

class PaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)