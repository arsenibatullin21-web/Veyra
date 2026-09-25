from django.contrib import admin
from django.db import transaction

from orders.models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'status', 'payment_status']

    def save_model(self, request, obj, form, change):
        old_status = None

        if change:
            old_status = Order.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if change and old_status != obj.status:
            transaction.on_commit(
                lambda: send_order_status_email.delay(obj.pk)
            )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_variant', 'price', 'quantity']


