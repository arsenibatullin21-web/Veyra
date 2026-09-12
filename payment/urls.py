from django.contrib import admin
from django.urls import path, include

from payment import views
from . import webhooks
app_name = 'payment'
urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook', webhooks.payment_webhook, name='webhook')
]