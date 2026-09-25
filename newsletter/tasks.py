from smtplib import SMTPException

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from Veyra import settings
from newsletter.models import NewsletterSubscriber, Newsletter, NewsletterDelivery


@shared_task(retry_backoff=True, max_retries=3, autoretry_for=(SMTPException, ))
def send_subscribed_newsletter_email(subscribe_id):
    '''Email message user receives after subscribing to the Veyra newsletter'''
    subscriber = NewsletterSubscriber.objects.get(pk=subscribe_id)

    unsubscribe_link = (
        settings.SITE_URL
        + reverse('newsletter:unsubscribe', kwargs={'token': subscriber.token})
    )
    send_mail(
        subject='Subscribed to Veyra Newsletter',
        message=(
            f'Hello! You subscribed to Veyra Newsletter successfully.\n'
            'We will send important information to you email!\n\n'
            'If you want to unsubscribe use this link:\n'
            f'{unsubscribe_link}'
        ),
        html_message=(
                         '<p>Hello! You subscribed to Veyra Newsletter successfully.</p>'
                         '<p>We will send important information to you email!</p>'
                         '<p>If you want to unsubscribe use this link:</p>'
                         f'<p><a href="{unsubscribe_link}">Unsubscribe</a></p>'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email ],
        fail_silently=False
    )


@shared_task(retry_backoff=True, max_retries=3, autoretry_for=(SMTPException, ))
def send_newsletter_email(newsletter_id, domain, protocol):
    newsletter = Newsletter.objects.get(pk=newsletter_id)
    subscribers = NewsletterSubscriber.objects.filter(is_active=True)

    if not newsletter.is_ready_to_send or newsletter.sent_at:
        return

    for subscriber in subscribers:
        delivery, _ = NewsletterDelivery.objects.get_or_create(newsletter=newsletter, subscriber=subscriber)

        if delivery.sent_at:
            continue

        unsubscribe_link = (
                f'{protocol}://{domain}'
                + reverse('newsletter:unsubscribe', kwargs={'token': subscriber.token})
            )

        send_mail(
                subject=newsletter.subject,
                message=(
                    f'{newsletter.body}\n\n'
                    'If you want to unsubscribe use this link:\n'
                    f'{unsubscribe_link}'
                ),
                html_message=(
                    f'<p>{newsletter.subject}\n</p>'
                    f'<p>{newsletter.body}\n\n</p>'
                    '<p>If you want to unsubscribe use this link:\n</p>'
                    f'<p><a href="{unsubscribe_link}">Unsubscribe</a></p>'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=False
            )

        delivery.sent_at = timezone.now()
        delivery.save()

    newsletter.sent_at = timezone.now()
    newsletter.is_ready_to_send = False
    newsletter.save()

@shared_task(retry_backoff=True, max_retries=3, autoretry_for=(SMTPException, ))
def send_scheduled_newsletter_email():
    newsletters = Newsletter.objects.filter(is_ready_to_send=True, sent_at__isnull=True)

    for newsletter in newsletters:
        send_newsletter_email.delay(newsletter.pk)