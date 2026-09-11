from django import forms
from django.template.context_processors import request

from .models import Order

class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'order_type', 'comments']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        user = self.request.user
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.initial['first_name'] = user.first_name
            self.initial['last_name'] = user.last_name
            self.initial['email'] = user.email
            self.initial['phone'] = user.phone

    def save(self, commit = True):
        order = super().save(commit=False)

        if self.request.user and self.request.user.is_authenticated:
            order.user = self.request.user
        if commit:
            order.save()
        return order

    def clean(self):
        cleaned_data = super().clean()
        order_type = cleaned_data.get('order_type')

        if order_type == Order.OrderType.DELIVER:
            for field in ('city', 'postal_code', 'address'):
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for delivery.')
        elif order_type == Order.OrderType.PICKUP:
            cleaned_data['city'] = ''
            cleaned_data['postal_code'] = ''
            cleaned_data['address'] = ''

        return cleaned_data

