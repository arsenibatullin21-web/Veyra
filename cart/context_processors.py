from Veyra import settings


def cart_item_count(request):
    cart = request.session.get(settings.CART_SESSION_ID, {})
    return {
        'cart_item_count': sum(item.get('quantity', 0) for item in cart.values())
    }
