import uuid

from django.db import models

class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField()

    is_ready_to_send = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    token = models.UUIDField(
        default=uuid.uuid4
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'newsletter_subscriber'
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'

class NewsletterDelivery(models.Model):
    newsletter = models.ForeignKey(to='Newsletter', on_delete=models.CASCADE)
    subscriber = models.ForeignKey(to='NewsletterSubscriber', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['newsletter', 'subscriber'],
                name='unique_newsletter_deliver'
            )
        ]