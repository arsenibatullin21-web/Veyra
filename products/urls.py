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

]
