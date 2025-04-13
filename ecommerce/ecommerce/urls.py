"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from store import views
from django.conf import settings
from django.conf.urls.static import static
from store.views import toggle_wishlist, wishlist_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Route to the home page in the 'store' app
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', include('store.urls')),  # Include the 'store' app URLs
    path('verify-otp/<int:temp_user_id>/', views.verify_otp, name='verify_otp'),  # Make sure this is correct
    path('user-home/', views.user_home, name='user_home'),  # This is required
    
        path('products/brand/<str:brand>/', views.products_by_brand, name='products_by_brand'),
    path('products/category/<str:category_name>/', views.products_by_category, name='products_by_category'),
    path('search/', views.search_products, name='search_products'),

    path('toggle_wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('products/', views.display_products, name='display_products'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('get-product-sizes/<int:product_id>/', views.get_product_sizes, name='get_product_sizes'),

]
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)