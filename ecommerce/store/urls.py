from django.urls import path
from . import views
app_name = 'store'
urlpatterns = [
    path('', views.home, name='home'),  # Home page view
    path('register/', views.register, name='register'),  # Registration page view
    path('verify-otp/<int:temp_user_id>/', views.verify_otp, name='verify_otp'),  # Make sure this is correct
    path('login/', views.login_view, name='login'),  # Login page view
    # path('user/home/', views.user_home, name='user_home'),  # Ensure 'user_home' is named correctly
    path('category/<str:category>/', views.category_products, name='category_products'),
    path('user-home/', views.user_home, name='user_home'),  # Ensure this exists
    path('logout/', views.logout_view, name='logout'),

]
