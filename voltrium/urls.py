# voltrium/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_user,all_products,products_by_category,home,CustomLoginView,add_to_cart,view_cart,place_order,remove_from_cart

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_user, name='register_user'),
    path('products/', all_products, name='all_products'),
    path('products/<int:category_id>/', products_by_category, name='products_by_category'),
    path('login/', CustomLoginView, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('view-cart/', view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('place-order/', place_order, name='place_order'),
     path('remove_from_cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
]
