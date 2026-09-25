from django import forms

from newsletter.models import NewsletterSubscriber, Newsletter


class SubscribeNewsletterForm(forms.ModelForm):

    class Meta:
        model = NewsletterSubscriber
        fields = ['email']

    def clean(self):
        if NewsletterSubscriber.objects.filter(email=self.cleaned_data.get('email')).exists():
            raise forms.ValidationError('Email is already active.')

class CreateNewsletterForm(forms.ModelForm):

    class Meta:
        model = Newsletter
        fields = ['subject', 'body', 'is_ready_to_send']