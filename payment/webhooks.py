from decimal import Decimal

from django.db import transaction
from django.http import HttpResponse

import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import get_object_or_404

from orders.models import Order, OrderItem
from payment.models import PaymentAttempt
from products.models import ProductVariant



@csrf_exempt
def payment_webhook(request):
    pay_load = request.body
    sign_head = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload=pay_load,
            sig_header=sign_head,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        print(e)
        return HttpResponse(status=400)


    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            with transaction.atomic():
                try:
                   payment_attempt = PaymentAttempt.objects.get(token=session.client_reference_id, order__isnull=True)
                except PaymentAttempt.DoesNotExist:
                   return HttpResponse(200)
                order = Order.objects.create(
                    user=payment_attempt.user,
                    first_name=payment_attempt.first_name,
                    last_name=payment_attempt.last_name,
                    email=payment_attempt.email,
                    phone=payment_attempt.phone,
                    address=payment_attempt.address,
                    city=payment_attempt.city,
                    postal_code=payment_attempt.postal_code,
                    paid=True,
                    stripe_id=session.payment_intent,
                    payment_status=Order.PaymentStatus.PAID,
                    status=Order.OrderStatus.SHIPPED,
                    order_type=payment_attempt.order_type,
                    total_price=payment_attempt.total_price,
                    comments=payment_attempt.comments,
                )

                for item in payment_attempt.items:
                    product_variant = get_object_or_404(ProductVariant, pk=item['product_variant_id'])

                    OrderItem.objects.create(
                        order=order,
                        product_variant=product_variant,
                        price=Decimal(item['price']),
                        quantity=item['quantity'],
                    )

                    product_variant.stock -= item['quantity']
                    product_variant.save()

                payment_attempt.order = order
                payment_attempt.save(update_fields=['order'])
            return HttpResponse(200)
    return HttpResponse(status=200)

