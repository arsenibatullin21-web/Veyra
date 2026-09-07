from django.urls import path, include

from products import views

app_name = 'products'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('products/catalog/', views.CatalogPageView.as_view(), name='catalog'),
    path('products/detail/<str:product_slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='create'),
    path('products/detail/<str:product_slug>/update/', views.ProductUpdateView.as_view(), name='update'),
    path('products/detail/<str:product_slug>/delete/', views.ProductDeleteView.as_view(), name='delete'),


    path('api/v1/categories/', views.CategoryListDetailAPIView.as_view(), name='api-categories'),
    path('api/v1/categories/<int:category_id>/', views.CategoryListDetailAPIView.as_view(), name='api-categories-detail'),
    path('api/v1/category/create/', views.CategoryCreateUpdateAPIView.as_view(), name='api-category-create'),
    path('api/v1/category/<int:category_id>/update/', views.CategoryCreateUpdateAPIView.as_view(), name='api-category-update-delete'),


    path('api/v1/sizes/', views.SizeListDetailAPIView.as_view(), name='api-sizes'),
    path('api/v1/sizes/<int:size_id>/', views.SizeListDetailAPIView.as_view(), name='api-sizes-detail'),
    path('api/v1/sizes/create/', views.SizeCreateUpdateAPIView.as_view(), name='api-sizes-create'),
    path('api/v1/sizes/<int:size_id>/update/', views.SizeCreateUpdateAPIView.as_view(), name='api-sizes-update-delete'),

    path('api/v1/colors/', views.ColorListDetailAPIView.as_view(), name='api-colors'),
    path('api/v1/colors/<int:color_id>/', views.ColorListDetailAPIView.as_view(), name='api-colors-detail'),
    path('api/v1/colors/create/', views.ColorCreateUpdateAPIView.as_view(), name='api-colors-create'),
    path('api/v1/colors/<int:color_id>/update/', views.ColorCreateUpdateAPIView.as_view(), name='api-colors-update-delete'),

    path('api/v1/products/', views.ProductListDetailAPIView.as_view(), name='api-products'),
    path('api/v1/products/<int:product_id>/', views.ProductListDetailAPIView.as_view(), name='api-products-detail'),
    path('api/v1/products/create/', views.ProductCreateUpdateAPIView.as_view(), name='api-products-create'),
    path('api/v1/products/<int:product_id>/update/', views.ProductCreateUpdateAPIView.as_view(), name='api-products-update-delete'),

    path('api/v1/promocodes/', views.PromoCodeListAPIView.as_view(), name='api-promocodes'),
    path('api/v1/promocodes/create/', views.PromoCodeCreateUpdateAPIView.as_view(), name='api-promocodes-create'),
    path('api/v1/promocodes/<int:promocode_id>/update/', views.PromoCodeCreateUpdateAPIView.as_view(), name='api-promocodes-update-delete'),

    path('api/v1/productvariants/', views.ProductVariantsListDetailAPIView.as_view(), name='api-product_variants'),
    path('api/v1/productvariants/<int:product_variant_id>/detail/', views.ProductVariantsListDetailAPIView.as_view(), name='api-product_variants-detail'),
    path('api/v1/productvariants/create/', views.ProductVariantCreateUpdateAPIView.as_view(), name='api-product_variants-create'),
    path('api/v1/productvariants/<int:product_variant_id>/update/', views.ProductVariantCreateUpdateAPIView.as_view(), name='api-product_variants-update-delete'),





]
