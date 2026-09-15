from django.contrib.auth import get_user_model
from django.db import models

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ORDER_CREATED = 'order_created', "Order_Created"
        ORDER_PAID = 'order_paid', "Order_Paid"
        ORDER_CANCELED = 'order_canceled', "Order_Canceled"
        STOCK = 'stock', 'Stock'
        SYSTEM = 'system', 'System'

    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=120)
    type = models.CharField(choices=NotificationType.choices)
    message = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.user} -> {self.type}"

