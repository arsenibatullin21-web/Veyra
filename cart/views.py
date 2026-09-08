from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from cart.cart import Cart
from products.models import ProductVariant, PromoCode


@require_POST
def cart_add(request):
    product_id = request.POST.get('variant_id')
    cart = Cart(request)
    product_variant = get_object_or_404(ProductVariant, id=product_id)
    cart.add(product=product_variant)
    return redirect(product_variant.product.get_absolute_url())


def cart_detail(request):
    cart = Cart(request)
    promo = request.session.get('promo', None)
    promo_obj = None

    if promo:
        promo_obj = PromoCode.objects.filter(name=promo).first()

    subtotal = 0

    for item in cart:
        subtotal += item['product'].price * int(item['quantity'])
    discount = subtotal - cart.get_total(promo=promo_obj)

    if request.headers.get('HX-Request') == 'true':
        target = request.headers.get('HX-Target') == 'true'
        if target == 'msg':
            return render(request, 'partial/messages.html', {'cart': cart, 'cart_len': len(cart), 'promo_obj': promo_obj, 'subtotal': subtotal, 'discount': discount, 'total': cart.get_total(promo=promo_obj)})
        return render(request, 'partial/cart_response.html',{'cart': cart, 'cart_len': len(cart), 'promo_obj': promo_obj, 'subtotal': subtotal, 'discount': discount, 'total': cart.get_total(promo=promo_obj)})
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'cart_len': len(cart), 'promo_obj': promo_obj, 'subtotal': subtotal, 'discount': discount, 'total': cart.get_total(promo=promo_obj)})

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart:detail')

@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear_items()
    return redirect('cart:detail')

def cart_update_quantity(request, product_id):
    cart = Cart(request)
    action = request.GET.get('action')
    cart.update_quantity(product_id=product_id, action=action)
    return redirect('cart:detail')


def apply_promo(request):
    promocode = request.GET.get('promo')

    promo_object = PromoCode.objects.filter(name=promocode).first()

    if not promo_object:
        messages.error(request, "Promo code is invalid.")
        return redirect('cart:detail')
    request.session['promo'] = promo_object.name
    messages.success(request, 'Promo code was applied.')
    return redirect('cart:detail')


def remove_promo(request):
    promo = request.session.get('promo')

    if promo:
        del request.session['promo']
        request.session.modified = True
        messages.success(request, "Promo Code is removed.")
        return redirect('cart:detail')

    messages.error(request, 'There is no applied promo.')
    return redirect('cart:detail')
