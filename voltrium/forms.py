# myapp/forms.py
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Address,Review
from django.contrib.auth.hashers import check_password

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

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select())
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class AddressUpdateForm(forms.ModelForm):
    country = CountryField().formfield()

    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code', 'country']

class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='Old password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='New password confirmation', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not check_password(old_password, self.user.password):
            raise ValidationError('Your old password was entered incorrectly.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError('The two new password fields must match.')
        return cleaned_data