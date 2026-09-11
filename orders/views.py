from decimal import Decimal, ROUND_HALF_UP

from django.shortcuts import render, redirect

from cart.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import OrderItem
from products.models import PromoCode


def create_order(request):
    cart = Cart(request)
    promo = request.session.get('promo', None)
    promo_obj = None
    subtotal = 0

    for item in cart:
        subtotal += item['product'].price * int(item['quantity'])

    if promo:
        promo_obj = PromoCode.objects.filter(name=promo).first()
    total = cart.get_total(promo=promo_obj)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request=request)

        if form.is_valid():
            order = form.save()

            for item in cart:
                product = item['product']
                price = item['price']
                quantity = item['quantity']

                if promo_obj:
                    discount_amount = item['price'] * Decimal(promo_obj.discount) / Decimal("100")
                    price = (item['price'] - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                OrderItem.objects.create(
                    order=order,
                    product_variant=product,
                    price=price,
                    quantity=quantity
                )

                cart.clear_items()
                request.session['order_id'] = order.id
                return redirect('cart:detail')

            return render(request, 'orders/checkout.html', {
                'form': form,
                'total': total,
                'subtotal': subtotal,
                'cart': cart,
            })
    form = OrderCreateForm(request=request)
    return render(request, 'orders/checkout.html', {'form': form, 'total': total, 'subtotal': subtotal, 'cart': cart})


