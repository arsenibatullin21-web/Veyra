from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from jwt.utils import force_bytes


@shared_task(autoretry_for=(Exception, ), retry_backoff=True, max_retries=3)
def send_activation_email(user_id, domain, protocol):
    user = get_user_model().objects.get(pk=user_id)

    if user.is_active:
        return

    uidb64 = urlsafe_base64_encode(
        force_bytes(user.pk)
    )
    token = default_token_generator.make_token(user)

    activation_link = (
        f'{protocol}://{domain}'
        + reverse(

        'users:activate',
        kwargs={
            'uidb64': uidb64,
            'token': token
            }    ,
        )
    )

    send_mail(
        subject='Activate your Veyra Account',
        message=(
            f'Hello, {user.username}!\n\n'
            'Open this link to activate your account:\n'
            f'{activation_link}\n\n'
            'If you did not create this account, ignore this email.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )

@shared_task(retry_backoff=True, max_retries=3, autoretry_for=(SMTPException, ))
def send_password_changed_email(user_id):
    user = get_user_model().objects.get(pk=user_id)

    send_mail(
        subject="Password Change",
        message=(
            f'Hello, {user.username}!\n\n'
            'Your password was changed successfully!\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )