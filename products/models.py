from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

class Available(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(variants__stock__gt=0).distinct()

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to='categories/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "category"
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Size(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    position = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'size'
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)



class Color(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'
        db_table = 'color'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)




class Product(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    short_description = models.TextField(max_length=100, blank=True, null=True)
    main_image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.ForeignKey(to='Color', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    objects = models.Manager()
    group_code = models.SlugField(max_length=80, blank=True)
    available = Available()

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'product_slug': self.slug})

    @property
    def is_new(self):
        if self.created_at < self.created_at + timedelta(days=30):
            return True
        return False

    @property
    def is_sale(self):
        if self.variants.filter(discount__gt=0).exists():
            return True
        return False

    @property
    def available_sizes(self):
        return Size.objects.filter(products__product=self, products__stock__gt=0).distinct().order_by('position')

    @property
    def available_colors(self):
        return Color.objects.filter(pk=self.color_id)


class ProductVariant(models.Model):
    product = models.ForeignKey(to='Product', on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=0)
    size = models.ForeignKey(to='Size', on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    main_image = models.ImageField(upload_to='variants/', default='')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-product']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        db_table = 'product_variants'

    def __str__(self):
        return self.product.name


    @property
    def is_available(self):
        if self.stock == 0:
            return False
        return True

    @property
    def final_price(self):
        if self.discount:
            final = self.price - (self.price * Decimal(self.discount) / Decimal(100))
            return final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return self.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def is_new(self):
        if self.created_at < self.created_at + timedelta(days=30):
            return True
        return False





class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/gallery/')
    product = models.ForeignKey(to='Product', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f'{self.product} - {self.image.url}'


class PromoCode(models.Model):
    name = models.CharField(max_length=10, unique=True)
    discount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.name} - {self.discount}'

    class Meta:
        ordering = ['discount']
        verbose_name = 'PromoCode'
        verbose_name_plural = 'PromoCodes'
