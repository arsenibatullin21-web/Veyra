from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView

from newsletter.forms import SubscribeNewsletterForm, CreateNewsletterForm
from newsletter.models import NewsletterSubscriber, Newsletter
from newsletter.tasks import send_subscribed_newsletter_email, send_newsletter_email


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
            should_send_email = created

            if not created and not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
                should_send_email = True


            if should_send_email:
                protocol = 'https' if self.request.is_secure() else 'http'
                domain = self.request.get_host()

                transaction.on_commit(
                    lambda: send_subscribed_newsletter_email.delay(
                        subscriber.id,
                        domain,
                        protocol
                    )
                )

                messages.success(request, 'You subscribed successfully!')
            else:
                messages.success(request, 'You have already subscribed.')
        return redirect('products:home')


class UnsubscribeNewsletterView(View):
    def get(self, request, token):
        subscriber = get_object_or_404(
            NewsletterSubscriber,
            token=token
        )

        if subscriber.is_active:
            subscriber.is_active = False
            subscriber.save()
            messages.success(request, 'You unsubscribed successfully.')
        else:
            messages.error(request, 'You are already unsubscribed.')
        return redirect('products:home')


class NewsletterListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'newsletter/newsletter_list.html'
    context_object_name = 'newsletters'
    paginate_by = 12
    raise_exception = True

    def get_queryset(self):
        return Newsletter.objects.all().order_by('-created_at')

    def test_func(self):
        return self.request.user.is_staff

class AdminNewsletterSendView(LoginRequiredMixin, UserPassesTestMixin, View):
    raise_exception = True
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, newsletter_id):
        domain = self.request.get_host()
        protocol = 'https' if self.request.is_secure() else 'http'
        transaction.on_commit(
            lambda: send_newsletter_email.delay(
                newsletter_id,
                domain,
                protocol
            )
        )
        messages.success(request, 'Newsletter was sent successfully.')
        return redirect('newsletter:list')
