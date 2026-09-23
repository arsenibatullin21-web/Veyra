from django.urls import path
from . import views
app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.SubscribeNewsletterView.as_view(), name='subscribe'),
]