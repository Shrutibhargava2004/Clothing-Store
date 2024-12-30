from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),  # Home page view
    path('register/', views.register, name='register'),  # Registration page view
    path('login/', views.login_view, name='login'),  # Login page view
    path('user_home/', views.user_home, name='user_home'),  # User home page view
    path('category/<str:category>/', views.category_products, name='category_products'),

]
