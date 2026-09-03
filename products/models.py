from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify



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




class ProductVariant(models.Model):
    product = models.ForeignKey(to='Product', on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=0)
    size = models.ForeignKey(to='Size', on_delete=models.CASCADE, related_name='products')
    color = models.ForeignKey(to='Color', on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-product']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        db_table = 'product_variants'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'color', 'size'],
                name='unique_product_color_size'
            )
        ]

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
            return self.price - (self.price * self.discount / 100)
        return self.price




class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/gallery/')
    product = models.ForeignKey(to='ProductVariant', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f'{self.product.name} - {self.image.url}'


class PromoCode(models.Model):
    name = models.CharField(max_length=10, unique=True)
    discount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.name} - {self.discount}'

    class Meta:
        ordering = ['discount']
        verbose_name = 'PromoCode'
        verbose_name_plural = 'PromoCodes'

