from django.urls import path
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.MyNotificationsListView.as_view(), name='my'),
    path('read/<int:notification_id>/', views.read_notification, name='read'),
    path('read/all/', views.read_all_notifications, name='read_all')
]