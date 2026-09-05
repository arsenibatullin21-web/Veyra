from django import forms
from django.forms import inlineformset_factory

from products.models import Product, ProductVariant, ProductImage

ProductVariantCreateInlineFormSet = inlineformset_factory(
    parent_model=Product,
    model=ProductVariant,
    extra=2,
    can_delete=True,
    fields=['sku', 'price', 'discount', 'size', 'stock', 'main_image'],
    min_num=1,
    validate_min=True
)

ProductImageCreateInlineFormSet = inlineformset_factory(
    parent_model=Product,
    model=ProductImage,
    extra=2,
    can_delete=True,
    fields=['image']
)
class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'description', 'short_description', 'main_image', 'category', 'color', 'group_code']


ProductVariantUpdateInlineFormSet = inlineformset_factory(
    parent_model=Product,
    model=ProductVariant,
    fields=['sku', 'price', 'discount', 'size', 'stock', 'main_image'],
    can_delete=True
)

ProductImageUpdateInlineFormset = inlineformset_factory(
    parent_model=Product,
    model=ProductImage,
    fields=['image'],
    can_delete=True
)

class ProductUpdateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'description', 'short_description', 'main_image', 'category', 'color', 'group_code']