from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


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