from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create'),
    path('api/v1/orders/', views.OrderListAPIView.as_view(), name='api-orders'),
    path('api/v1/orders/<int:order_id>/detail/', views.OrderDetailAPIView.as_view(), name='api-orders-detail'),
    path('api/v1/orders/<int:order_id>/items/', views.OrderItemAPIView.as_view(), name='api-orders-items')
]