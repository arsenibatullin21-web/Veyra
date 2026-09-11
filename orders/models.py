from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from products.models import ProductVariant


class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
    class OrderType(models.TextChoices):
        PICKUP = 'pickup', 'Pickup'
        DELIVER = 'deliver', 'Deliver'


    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)
    payment_status = models.CharField(
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    order_type = models.CharField(
        choices=OrderType.choices,
        default=OrderType.PICKUP
    )
    status = models.CharField(
        choices=OrderStatus.choices,
        default=PaymentStatus.PENDING,
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comments = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order: {self.id}'

    @property
    def get_total_cost(self):
        return sum(item.get_cost for item in self.items.all())

    def get_stripe_url(self):
        if not self.stripe_id:
            return ''
        if 'test' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = ''
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(to='Order', on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(to=ProductVariant, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'

    def __str__(self):
        return f"{self.product_variant.product.name} X {self.quantity}"

    @property
    def get_cost(self):
        return self.price * self.quantity

