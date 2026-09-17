from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.serializers import AdminNotificationListSerializer, MyNotificationListSerializer
from products.permissions import IsStaff


class MyNotificationsListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        filter_type = self.request.GET.get('filter_type')

        if filter_type == 'unread':
            queryset = queryset.filter(is_read=False)

        return queryset


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['unread'] = Notification.objects.filter(is_read=False, user=self.request.user)
        context['filter_type'] = self.request.GET.get('filter_type')
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request') == 'true':
            return ['notifications/partial/notification_partial.html']
        return ['notifications/notifications.html']


@require_POST
def read_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    unread = Notification.objects.filter(is_read=False, user=request.user)
    queryset = Notification.objects.filter(user=request.user)
    filter_type = request.POST.get('filter_type')

    if filter_type == 'unread':
        queryset = queryset.filter(is_read=False)

    return render(request, 'notifications/partial/notification_partial.html', {'unread': unread, 'notifications': queryset, 'filter_type': filter_type})

@require_POST
def read_all_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)

    for notification in notifications:
        notification.is_read = True
        notification.save(update_fields=['is_read'])

    unread = Notification.objects.filter(is_read=False, user=request.user)
    queryset = Notification.objects.filter(user=request.user)
    filter_type = request.POST.get('filter_type')

    if filter_type == 'unread':
        queryset = queryset.filter(is_read=False)

    return render(request, 'notifications/partial/notification_partial.html', {'unread': unread, 'notifications': queryset, 'filter_type': filter_type})


class NotificationListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff and self.kwargs.get('user_id'):
            user = get_object_or_404(get_user_model(), pk=self.kwargs.get('user_id'))
            return Notification.objects.filter(user=user).order_by('-created_at')

        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return AdminNotificationListSerializer
        return MyNotificationListSerializer

class ReadNotificationApiView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    def post(self, request, *args, **kwargs):
        notification_id = kwargs.get('notification_id')
        if notification_id:
            queryset = Notification.objects.all()
            if not request.user.is_staff:
                queryset = queryset.filter(user=request.user)

            notification = get_object_or_404(queryset, pk=notification_id)

            if not notification.is_read:
                notification.is_read = True
                notification.save(update_fields=['is_read'])
                return Response({
                    'message': f'Notification #{notification.id} marked as read.'
                })
            return Response({
                'message': f'Notification #{notification.id} is already read.'
            })

        Notification.objects.filter(user=self.request.user, is_read=False).update(is_read=True)
        return Response({
            'message': 'All notifications marked as read.'
        })
