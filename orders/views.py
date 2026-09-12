from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied as PermissionDeniedDrf

from cart.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import OrderItem, Order
from orders.serializers import OrderListSerializer, OrderDetailSerializer, UserOrderListSerializer, \
    UserOrderDetailSerializer, OrderItemSerializer, UserOrderItemSerializer
from payment.models import PaymentAttempt
from products.models import PromoCode
from products.permissions import IsStaff


@login_required
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
            items = []


            for item in cart:
                product = item['product']
                price = item['price']
                quantity = item['quantity']
                if promo_obj:
                    discount_amount = item['price'] * Decimal(promo_obj.discount) / Decimal("100")
                    price = (item['price'] - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                items.append({
                    'product_variant_id': str(product.id),
                    'price': str(price),
                    'quantity': int(quantity)
                })


            payment_attempt = PaymentAttempt.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                total_price=total,
                comments=form.cleaned_data['comments'],
                order_type=form.cleaned_data['order_type'],
                items=items
            )

            request.session['payment_token'] = str(payment_attempt.token)
            return redirect('payment:process')

        return render(request, 'orders/checkout.html', {
                'form': form,
                'total': total,
                'subtotal': subtotal,
                'cart': cart,
            })
    form = OrderCreateForm(request=request)
    return render(request, 'orders/checkout.html', {'form': form, 'total': total, 'subtotal': subtotal, 'cart': cart})


class MyOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/my_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class MyOrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    pk_url_kwarg = "order_id"

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related(
                "items__product_variant__product",
                "items__product_variant__size",
            )
        )


class OrderListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderListSerializer
        return UserOrderListSerializer

class OrderDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'order_id'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderDetailSerializer
        return UserOrderDetailSerializer


class OrderItemAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]


    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderItemSerializer
        return UserOrderItemSerializer

    def get_queryset(self):
        orders = Order.objects.all()
        if not self.request.user.is_staff:
            orders = orders.filter(user=self.request.user)

        order = get_object_or_404(
            orders,
            pk=self.kwargs.get('order_id')
        )
        return OrderItem.objects.filter(order=order)
