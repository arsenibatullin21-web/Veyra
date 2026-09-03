from django.contrib import admin

from products.models import Category, Product, Size, Color, ProductVariant, ProductImage, PromoCode


class ProductImageInline(admin.TabularInline):
    extra = 3
    model = ProductImage

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'position']
    prepopulated_fields = {'slug': ('name', )}

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'hex_code']
    prepopulated_fields = {'slug': ('name', )}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name', )}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'short_description']
    prepopulated_fields = {'slug': ('name', )}

@admin.register(ProductVariant)
class ProductVariant(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount']


