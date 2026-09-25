from django.urls import path
from . import views
app_name = 'newsletter'

urlpatterns = [
    path('', views.NewsletterListView.as_view(), name='list'),
    path('subscribe/', views.SubscribeNewsletterView.as_view(), name='subscribe'),
    path('unsubscribe/<token>/', views.UnsubscribeNewsletterView.as_view(), name='unsubscribe'),

    path('send/<int:newsletter_id>/', views.AdminNewsletterSendView.as_view(), name='send')
]
