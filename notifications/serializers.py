from rest_framework import serializers
from .models import Notification
from django.utils.timesince import timesince

class AdminNotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'type', 'message', 'is_read', 'created_at']

class MyNotificationListSerializer(serializers.ModelSerializer):
    sent_at = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'title', 'type', 'message', 'is_read', 'sent_at']

    def get_sent_at(self, obj):
        return f"{timesince(obj.created_at)}"



