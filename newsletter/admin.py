from django.contrib import admin

from newsletter.models import Newsletter, NewsletterSubscriber, NewsletterDelivery

admin.site.register(Newsletter)
admin.site.register(NewsletterSubscriber)
admin.site.register(NewsletterDelivery)
