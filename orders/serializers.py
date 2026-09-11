from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Order
        fields = ['id','user', 'full_name', 'order_type','payment_status', 'status', 'get_total_cost']

    def get_full_name(self, obj):
        return obj.user.first_name + '' + obj.user.last_name


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_variant', 'price', 'quantity', 'get_cost']

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'paid', 'stripe_id', 'payment_status', 'order_type', 'status', 'get_total_cost', 'comments','created_at', 'updated_at', 'items']


class UserOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_variant', 'price', 'quantity']

class UserOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','email', 'phone', 'order_type','get_total_cost']

class UserOrderDetailSerializer(serializers.ModelSerializer):
    items = UserOrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'payment_status', 'status', 'order_type', 'get_total_cost', 'comments', 'items']