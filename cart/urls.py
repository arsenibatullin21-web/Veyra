from django.contrib import admin
from django.urls import path, include

from cart import views

app_name = 'cart'

urlpatterns = [
    path('add/', views.cart_add, name='add'),
    path('', views.cart_detail, name='detail'),
    path('remove/promo/', views.remove_promo, name='remove-promo'),
    path('remove/<str:product_id>/', views.cart_remove, name='remove'),
    path('clear/', views.cart_clear, name='clear'),
    path('upd_quantity/<str:product_id>/', views.cart_update_quantity, name='update'),
    path('apply/promo/', views.apply_promo, name='appy-promo'),
]
