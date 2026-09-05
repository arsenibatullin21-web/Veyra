from django.urls import path, include

from products import views

app_name = 'products'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('products/catalog/', views.CatalogPageView.as_view(), name='catalog'),
    path('products/detail/<str:product_slug>/', views.ProductDetailView.as_view(), name='detail')
]