from decimal import Decimal
from django.contrib import messages
import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from Veyra import settings
from cart.cart import Cart
from orders.models import Order
from payment.models import PaymentAttempt
from products.models import ProductVariant

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def payment_process(request):
    payment_token = request.session.get('payment_token', None)
    payment_attempt = get_object_or_404(PaymentAttempt, token=payment_token)

    success_url = request.build_absolute_uri(
        reverse('payment:success')
    )
    cancel_url = request.build_absolute_uri(
        reverse('payment:cancel')
    )


    session_data = {
        'mode': 'payment',
        'client_reference_id': str(payment_attempt.token),
        'success_url': success_url,
        'cancel_url': cancel_url,
        'line_items': []
    }

    for item in payment_attempt.items:
        product_variant = get_object_or_404(ProductVariant, pk=int(item['product_variant_id']))
        session_data['line_items'].append({
            'price_data': {
                'unit_amount': int(Decimal(item['price']) * Decimal('100')),
                'currency': 'usd',
                'product_data': {
                    'name': product_variant.product.name
                }
            },
            'quantity': item['quantity']
        })

    session = stripe.checkout.Session.create(**session_data)
    payment_attempt.stripe_id = session.id
    payment_attempt.save()
    return redirect(session.url, code=303)


def payment_success(request):
    cart = Cart(request)
    payment_attempt = get_object_or_404(
        PaymentAttempt,
        token=request.session.get('payment_token')
    )
    if payment_attempt.order_id:
        cart.clear_items()
        messages.success(request, "Payment completed successfully")
    else:
        messages.success(request, "Payment is being confirmed")
    return redirect(
        'orders:my_orders'
    )

def payment_cancel(request):
    messages.error(request, "Something went wrong.")
    return redirect(
        'orders:create'
    )

