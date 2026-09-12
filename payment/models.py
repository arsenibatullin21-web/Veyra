import uuid

from django.contrib.auth import get_user_model
from django.db import models

class PaymentAttempt(models.Model):
    class OrderType(models.TextChoices):
        PICKUP = 'pickup', 'Pickup'
        DELIVER = 'deliver', 'Deliver'

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="payment_attempts"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_id = models.CharField(max_length=250, blank=True)
    items = models.JSONField()
    order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.PICKUP
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comments = models.TextField(max_length=500, null=True, blank=True)
    order = models.OneToOneField(to="orders.Order",  on_delete=models.CASCADE, related_name='payment_attempts', null=True, blank=True)