from django.db import transaction
from rest_framework import serializers

from products.models import Product, Category, ProductVariant, Size, Color, PromoCode, ProductImage


class CategoryListDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'created_at', 'updated_at']


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug','description', 'image', 'created_at']
        read_only_fields = ['slug', 'created_at']

class SizeListDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Size
        fields = ['id','name', 'slug', 'position', 'created_at', 'updated_at']

class SizeCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Size
        fields = ['name', 'position']


class ColorListDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Color
        fields = ['id', 'name', 'slug', 'hex_code', 'created_at', 'updated_at']


class PromoCodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['id', 'name', 'discount']

class PromoCodeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['name', 'discount']


class ColorCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name', 'hex_code']


class ProductImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image']






class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','sku', 'price', 'discount', 'size', 'stock', 'main_image']
        read_only_fields = ['id']



class ProductVariantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','product', 'sku', 'price', 'discount', 'size', 'stock', 'main_image']

class ProductVariantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','product', 'sku','price', 'discount', 'final_price', 'size', 'stock', 'main_image', 'is_new', 'is_available', 'updated_at', 'created_at']












class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name', 'slug', 'short_description', 'main_image', 'category', 'color', 'group_code']



class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageListSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    available_colors = serializers.SerializerMethodField(read_only=True)
    available_sizes = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = ['name', 'slug', 'short_description', 'description', 'main_image', 'category', 'color', 'group_code', 'is_new', 'is_sale', 'available_colors', 'available_sizes', 'updated_at', 'created_at', 'images', 'variants']

    def get_available_sizes(self, obj):
        return SizeListDetailSerializer(
            obj.available_sizes,
            many=True
        ).data

    def get_available_colors(self, obj):
        return ColorListDetailSerializer(
            obj.available_colors,
            many=True
        ).data

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, required=False)
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug','short_description', 'description', 'category', 'main_image', 'color', 'group_code', 'variants', 'updated_at', 'created_at']
        read_only_fields = ['id', 'slug', 'updated_at', 'created_at']

    def create(self, validated_data):
        variants = validated_data.pop('variants', [])

        with transaction.atomic():
            product = Product.objects.create(**validated_data)

            for variant in variants:
                ProductVariant.objects.create(product=product, **variant)

        return product


    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for variant_data in variants_data:
            variant_id = variant_data.get('id')
            variant = ProductVariant.objects.get(id=variant_id, product=instance)

            for attr, value in variant_data.items():
                setattr(variant, attr, value)
            variant.save()
        return instance

