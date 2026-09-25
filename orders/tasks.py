from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from orders.models import Order


@shared_task(retry_backoff=True, max_retries=3, autoretry_for=(SMTPException, ))
def send_created_order_email(user_id):
    user = get_user_model().objects.get(pk=user_id)

    send_mail(
        subject='New Order!',
        message=(
            f'Your order was payed successfully\n'
            'You will get it soon'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email, ],
        fail_silently=False
    )

@shared_task(retry_backoff=True, max_retries=3, autoretry_for=(SMTPException, ))
def send_order_status_email(order_id):
    order = Order.objects.get(pk=order_id)

    send_mail(
        subject='Order status changed',
        message=(
            f'Order status was changed to {order.status}\n'
            'You will get your order soon.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email, ],
        fail_silently=False
    )