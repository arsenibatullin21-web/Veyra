from django.urls import path
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.MyNotificationsListView.as_view(), name='my'),
    path('read/<int:notification_id>/', views.read_notification, name='read'),
    path('read/all/', views.read_all_notifications, name='read_all'),

    path('api/v1/notifications/', views.NotificationListAPIView.as_view(), name='api-notifications'),
    path('api/v1/notifications/<int:user_id>/', views.NotificationListAPIView.as_view(), name='api-notifications-admin'),
    path('api/v1/notifications/read/<int:notification_id>/', views.ReadNotificationApiView.as_view(), name='api-read'),
    path('api/v1/notifications/read/all/', views.ReadNotificationApiView.as_view(), name='api-read-all'),
]
