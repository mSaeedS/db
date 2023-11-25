# voltrium/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.views import View
from .forms import UserRegistrationForm,AddressForm
from .models import User,Address

def register_user(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            user = user_form.save()  # Save the user data
            address = address_form.save(commit=False)
            address.user = user  # Associate the address with the user
            address.save()  # Save the address data

            # Additional logic can be added here, such as sending a welcome email.
            return redirect('registration_success')
    else:
        user_form = UserRegistrationForm()
        address_form = AddressForm()

    return render(request, 'registration/register_user.html', {'user_form': user_form, 'address_form': address_form})

def registration_success(request):
    return render(request, 'registration/registration_success.html')





