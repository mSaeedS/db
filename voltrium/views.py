# voltrium/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.views import View
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm,AddressForm
from .models import User,Address,Product,Category
from django.contrib import messages

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
            return redirect('home')
        else:
            print(f"User Form Errors: {user_form.errors}")
            print(f"Address Form Errors: {address_form.errors}")
    else:
        user_form = UserRegistrationForm()
        address_form = AddressForm()

    return render(request, 'registration/register_user.html', {'user_form': user_form, 'address_form': address_form})

def registration_success(request):
    return render(request, 'registration/registration_success.html')



def all_products(request):
    products = Product.objects.all()
    return render(request, 'product/all_products.html', {'products': products})

def products_by_category(request, category_id):
    category = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'product/products_by_category.html', {'products': products, 'category': category})

def home(request):
    return render(request, 'home.html')







