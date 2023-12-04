# voltrium/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm,AddressForm,CustomAuthenticationForm,PaymentForm,ReviewForm,CustomPasswordChangeForm
from .models import User,Address,Product,Category,CartItem,Order,OrderLine,Payment,Review
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db.models import F,Sum
from django.utils import timezone
from django.db import transaction



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
                    # Update order line to indicate that a review can be submitted
                    order_line = OrderLine.objects.get(order=order, product=cart_item.product)
                    order_line.review_submitted = True
                    order_line.save()
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
                    # Update order line to indicate that a review can be submitted
                    order_line = OrderLine.objects.get(order=order, product=cart_item.product)
                    order_line.review_submitted = True
                    order_line.save()
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

def product_detail(request, product_id):
    from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review, OrderLine

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user

    # Check if the user has ordered the product and is eligible to submit a review
    has_ordered = False

    if user.is_authenticated:
        has_ordered = OrderLine.objects.filter(
            order__user=user,
            product=product,
            review_submitted=True
        ).exists()

    reviews = Review.objects.filter(product=product)

    if request.method == 'POST' and has_ordered:
        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = user
            review.save()

            # Mark the order line as review submitted
            order_line = OrderLine.objects.get(
                order__user=user,
                product=product,
                review_submitted=True
            )
            order_line.review_submitted = False
            order_line.save()

            # Redirect to the product detail page after a successful submission
            return redirect('product_detail', product_id=product.id)

    else:
        review_form = ReviewForm()

    return render(request, 'product/product_detail.html', {
        'product': product,
        'has_ordered': has_ordered,
        'review_form': review_form,
        'reviews': reviews
    })

def profile(request):
    user = request.user

<<<<<<< HEAD
    # Fetch user's addresses
=======
>>>>>>> 2c27153335ef95b759d64264d0a04c541b666d87
    addresses = Address.objects.filter(user=user)
    if addresses:
        address_instance = addresses.first()
    else:
        address_instance = Address(user=user)

    address_form = AddressForm(request.POST or None, instance=address_instance)

<<<<<<< HEAD
    # Fetch user's order lines and orders
    order_lines = OrderLine.objects.filter(order__user=user)
    orders = Order.objects.filter(user=user)

    context = {
        'address_form': address_form,
        'addresses': addresses,
        'order_lines': order_lines,
        'orders': orders
    }

=======
>>>>>>> 2c27153335ef95b759d64264d0a04c541b666d87
    if request.method == 'POST':
        if 'address_submit' in request.POST:
            if address_form.is_valid():
                address_form.save()
                messages.success(request, 'Your address was successfully updated.')
                return redirect('home')

<<<<<<< HEAD
=======
    context = {
        'address_form': address_form,
        'addresses': addresses
    }
>>>>>>> 2c27153335ef95b759d64264d0a04c541b666d87
    return render(request, 'profile.html', context)

def password_change(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page or appropriate URL

    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Hash the new password
            new_password = make_password(form.cleaned_data['new_password1'])

            # Set and save the new password
            request.user.password = new_password
            request.user.save()

            # Update the session hash to keep the user logged in
            update_session_auth_hash(request, request.user)

            # Display a success message and redirect
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Replace with the appropriate URL where the user should be redirected

    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'password_change.html', {'form': form})





