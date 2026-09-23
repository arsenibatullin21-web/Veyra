from django.db import transaction
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from newsletter.forms import SubscribeNewsletterForm
from newsletter.models import NewsletterSubscriber


# Create your views here.
class SubscribeNewsletterView(View):
    def post(self, request, *args, **kwargs):
        form = SubscribeNewsletterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )

            if not created and not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()

                messages.success(request, 'You subscribed successfully!')
            else:
                messages.success(request, 'You have already subscribed.')
        return redirect('products:home')