
from django.contrib import admin
from .models import Product, Category,User, Order, Address, CartItem, Payment, Review
# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(Review)