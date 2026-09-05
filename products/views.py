from sys import prefix

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Min
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from products.forms import ProductCreateForm, ProductVariantCreateInlineFormSet, ProductImageCreateInlineFormSet, \
    ProductUpdateForm, ProductVariantUpdateInlineFormSet, ProductImageUpdateInlineFormset
from products.models import Product, Category, ProductImage, ProductVariant, Size, Color
from products.services import create_product_with_variant, update_product_with_variant


class HomePageView(ListView):
    model = Product
    template_name = 'products/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(variants__stock__gt=0).distinct()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['categories'] = Category.objects.all()
        return context

class CatalogFilterMixin:

    def get_sorted_queryset(self, request):
        queryset = Product.available.all()

        category = request.GET.getlist('category')
        size = request.GET.getlist('size')
        price = request.GET.get('price')
        sort = request.GET.get('sort')

        if category:
            queryset = queryset.filter(category__slug__in=category)

        if size:
            queryset = queryset.filter(variants__size__slug__in=size).distinct()

        if price and price != 'all':
            if price == 'under-50':
                queryset = queryset.filter(variants__price__lt=50).distinct()
            elif price == '50-100':
                queryset = queryset.filter(variants__price__gte=50, variants__price__lte=100).distinct()
            elif price == 'sale':
                queryset = queryset.filter(variants__discount__gt=0).distinct()

        if sort:
            if sort == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort == 'low-to-high':
                queryset = queryset.annotate(min_price=Min('variants__price')).order_by('min_price')
            elif sort == 'high-to-low':
                queryset = queryset.annotate(min_price=Min('variants__price')).order_by('-min_price')

        return queryset


class CatalogPageView(CatalogFilterMixin, ListView):
    model = Product
    template_name = 'products/catalog.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_template_names(self):
        if self.request.headers.get('HX-Request') == 'true':
            if self.request.GET.get('page'):
                return ['products/partial/product-list.html']
            return ['products/partial/catalog-partial.html']

        return ['products/catalog.html']

    def get_queryset(self):
        queryset = self.get_sorted_queryset(self.request)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['variants'] = ProductVariant.objects.filter(stock__gt=0)
        context['on_sale'] = ProductVariant.objects.filter(discount__gt=0)
        context['categories'] = Category.objects.all()
        context['sizes'] = Size.objects.all().order_by('position')
        context['colors'] = Color.objects.all()
        context['selected_categories'] = self.request.GET.getlist('category')
        context['selected_sizes'] = self.request.GET.getlist('size')
        context['selected_price'] = self.request.GET.get('price')
        context['selected_sort'] = self.request.GET.get('sort')
        querydict = self.request.GET.copy()
        querydict.pop('page', None)
        context['querystring'] = querydict.urlencode()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.group_code:
            context['color_products'] = Product.available.filter(
                group_code=self.object.group_code
            ).select_related('color').order_by('color__name')
        else:
            context['color_products'] = Product.available.filter(pk=self.object.pk).select_related('color')
        return context

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    template_name = 'products/product_create.html'
    form_class = ProductCreateForm

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('products:catalog')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variant_form'] = ProductVariantCreateInlineFormSet(
            self.request.POST or None,
            self.request.FILES or None,
            prefix='variants',
            instance=self.object
        )
        context['image_form'] = ProductImageCreateInlineFormSet(
            self.request.POST or None,
            self.request.FILES or None,
            prefix='images',
            instance=self.object
        )
        return context

    def form_valid(self, form):
        variant_form = ProductVariantCreateInlineFormSet(
            data=self.request.POST,
            files=self.request.FILES,
            prefix='variants',
            instance=self.object
        )

        image_form = ProductImageCreateInlineFormSet(
            data=self.request.POST,
            files=self.request.FILES,
            prefix='images',
            instance=self.object
        )

        product, result = create_product_with_variant(form_image=image_form, form=form, formset=variant_form)

        if result == 'InvalidForm':
            return self.form_invalid(form)

        if result == 'InvalidFormset':
            return self.form_invalid(form)

        if result == 'InvalidFormImage':
            return self.form_invalid(form)
        
        self.object = product
        return HttpResponseRedirect(self.get_success_url())


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'products/product_update.html'
    form_class = ProductUpdateForm
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variant_form'] = ProductVariantUpdateInlineFormSet(
            self.request.POST or None,
            self.request.FILES or None,
            prefix='variants',
            instance=self.object
        )
        context['image_form'] = ProductImageUpdateInlineFormset(
            self.request.POST or None,
            self.request.FILES or None,
            prefix='images',
            instance=self.object
        )
        return context

    def form_valid(self, form):
        variant_form = ProductVariantUpdateInlineFormSet(
            data=self.request.POST,
            files=self.request.FILES,
            prefix='variants',
            instance=self.object
        )
        image_form = ProductImageUpdateInlineFormset(
            data=self.request.POST,
            files=self.request.FILES,
            prefix='images',
            instance=self.object
        )


        product, result = update_product_with_variant(form_image=image_form, form=form, formset=variant_form)

        if result == 'InvalidForm':
            return self.form_invalid(form)

        if result == 'InvalidFormset':
            return self.form_invalid(form)

        if result == 'InvalidFormImage':
            return self.form_invalid(form)

        self.object = product
        return HttpResponseRedirect(self.get_success_url())


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    slug_url_kwarg = 'product_slug'
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('products:catalog')

    def test_func(self):
        return self.request.user.is_staff
    
