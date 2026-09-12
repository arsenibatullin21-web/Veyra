from django.contrib import admin

from payment.models import PaymentAttempt


# Register your models here.
@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'email']