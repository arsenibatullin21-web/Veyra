from django import forms

from newsletter.models import NewsletterSubscriber


class SubscribeNewsletterForm(forms.ModelForm):

    class Meta:
        model = NewsletterSubscriber
        fields = ['email']

    def clean(self):
        if NewsletterSubscriber.objects.filter(email=self.cleaned_data.get('email')).exists():
            raise forms.ValidationError('Email is already active.')