# voltrium/urls.py
from django.urls import path
from .views import register_user,registration_success,all_products,products_by_category,home

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_user, name='register_user'),
    path('registration-success/', registration_success, name='registration_success'),
    path('products/', all_products, name='all_products'),
    path('products/<int:category_id>/', products_by_category, name='products_by_category'),
    
 
]
