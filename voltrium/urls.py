# voltrium/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_user,all_products,products_by_category,home,CustomLoginView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_user, name='register_user'),
    path('products/', all_products, name='all_products'),
    path('products/<int:category_id>/', products_by_category, name='products_by_category'),
    path('login/', CustomLoginView, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
