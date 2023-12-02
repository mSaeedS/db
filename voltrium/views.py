# voltrium/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm,AddressForm,CustomAuthenticationForm,PaymentForm
from .models import User,Address,Product,Category,CartItem,Order,OrderLine,Payment
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db.models import F,Sum
from django.utils import timezone
from django.db import transaction

def register_user(request):
    from django.contrib.auth.hashers import make_password

def register_user(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            user = user_form.save(commit=False)
            
            # Hash the password before saving the user
            user.password = make_password(user_form.cleaned_data['password'])

            user.save()  # Save the user data
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



def all_products(request):
    products = Product.objects.all()
    return render(request, 'product/all_products.html', {'products': products})

def products_by_category(request, category_id=None):
    if category_id:
        category = Category.objects.get(pk=category_id)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()
    
    return render(request, 'product/products_by_category.html', {'products': products, 'categories': categories})

def home(request):
    return render(request, 'home.html')

def CustomLoginView(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request,username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                print("Authentication failed: User does not exist or incorrect password.")

    else:
        form = CustomAuthenticationForm(request)

    return render(request, 'registration/login.html', {'form': form})

def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']

            # Start a transaction
            with transaction.atomic():
                # Create a new order
                order = Order.objects.create(user=request.user, total_amount=0)

                # Loop through cart items and create order lines
                for cart_item in cart_items:
                    if cart_item.quantity > cart_item.product.stock_quantity:
                        # Insufficient stock, do not proceed with order
                        messages.error(request, f"Not enough stock for {cart_item.product.name}.")
                        return redirect('view_cart')

                    OrderLine.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price
                    )

                    # Update product stock
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()

                # Calculate and update total amount for the order
                total_amount = order.orderline_set.aggregate(
                    total=Sum(F('unit_price') * F('quantity'))
                )['total'] or 0
                order.total_amount = total_amount
                order.save()

                # Create a payment record
                Payment.objects.create(user=request.user, order=order, payment_method=payment_method)

                # Clear the user's cart
                cart_items.delete()

                messages.success(request, "Your order has been placed successfully.")
                return redirect('home')  # Redirect to a success page

    else:
        form = PaymentForm()

    return render(request, 'product/view_cart.html', {'cart_items': cart_items, 'payment_form': form})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Check if the product is out of stock
    if product.stock_quantity <= 0:
        # Handle the case where the product is out of stock
        messages.error(request, "This product is currently out of stock.")
        return redirect('all_products')  # Assuming 'all_products' is the view name for displaying all products

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    # Increment the quantity if the item is already in the cart and stock is available
    if not created and cart_item.quantity < product.stock_quantity:
        cart_item.quantity += 1
        cart_item.save()
    elif not created:
        # Handle the case where the requested quantity exceeds the stock
        messages.error(request, "Not enough stock available.")
        return redirect('all_products')  # Assuming 'product_detail' is the view name for a single product

    return redirect('view_cart')  # Redirect to the cart view

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)

    # Remove the item from the cart
    cart_item.delete()
    # Optionally, you can add a success message
    messages.success(request, 'Item has been removed from your cart.')
    # Render the confirmation template
    return render(request, 'product/remove_from_cart.html')

@transaction.atomic
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Start a transaction
            with transaction.atomic():
                # Create a new order
                order = Order.objects.create(user=request.user, total_amount=0)

                # Loop through cart items, create order lines, and update stock
                for cart_item in cart_items:
                    if cart_item.quantity > cart_item.product.stock_quantity:
                        # Insufficient stock, do not proceed with order
                        messages.error(request, f"Not enough stock for {cart_item.product.name}.")
                        return redirect('view_cart')

                    OrderLine.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price
                    )

                    # Update product stock
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()

                # Calculate the total amount for the order
                order.total_amount = sum(line.unit_price * line.quantity for line in order.orderline_set.all())
                order.save()

                # Create a payment record
                Payment.objects.create(user=request.user, order=order, payment_method=form.cleaned_data['payment_method'])

                # Clear the user's cart
                cart_items.delete()

                messages.success(request, "Your order has been placed successfully.")
                return redirect('home')  # Or any other success page

    else:
        form = PaymentForm()

    return render(request, 'product/view_cart.html', {'cart_items': cart_items, 'payment_form': form})



