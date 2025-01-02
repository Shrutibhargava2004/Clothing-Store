from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import Product, Category, TempUser , Order, ProductSize, Wishlist
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from .forms import RegisterForm, LoginForm 
import random, json
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # For complex queries like search



# Home page view
def home(request):
    return render(request, 'store/home.html')

@csrf_exempt
# Login view (fixed for email authentication)
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate user
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "You are now logged in!")
                    return redirect('user_home')  # Redirect to the correct URL name
                else:
                    messages.error(request, 'Invalid credentials. Please try again.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials. Please try again.')
        else:
            messages.error(request, 'Please check the form for errors.')
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})

@csrf_exempt
# Register view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Generate OTP
            otp = generate_otp()
            
            # Create temporary user record
            temp_user = TempUser.objects.create(username=username, email=email, password=password, otp=otp)
            
            # Send OTP email to the user
            send_otp_email(email, otp)
            
            # Redirect to OTP verification page
            return redirect('store:verify_otp', temp_user_id=temp_user.id)
    
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})

# Generate OTP function
def generate_otp():
    return get_random_string(length=6, allowed_chars='0123456789')

# Send OTP email function
def send_otp_email(user_email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP for registration is: {otp}'
    send_mail(subject, message, 'bhargavareadymade1962@gmail.com', [user_email])

# OTP verification view
def verify_otp(request, temp_user_id):
    try:
        # Fetch the temporary user record
        temp_user = TempUser.objects.get(id=temp_user_id)
    except TempUser.DoesNotExist:
        messages.error(request, "Invalid OTP record.")
        return redirect('store:register')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        # Check if the entered OTP matches the one stored in the TempUser record
        if entered_otp == temp_user.otp:
            # OTP is correct, create the user
            user = User.objects.create_user(username=temp_user.username, email=temp_user.email, password=temp_user.password)
            
            # Delete the temporary user record after successful registration
            temp_user.delete()
            
            messages.success(request, "Registration successful!")
            return redirect('login')  # Redirect to login page after successful registration
        else:
            messages.error(request, "Incorrect OTP. Please try again.")
    
    return render(request, 'store/verify_otp.html', {'temp_user_id': temp_user_id})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')  # Redirect to home or login page after logout

# def user_home(request):
#     categories = Category.objects.all()  # Fetch all categories from the database
#     return render(request, 'store/user_home.html', {'categories': categories})
@login_required
def user_home(request):
    unique_brands = Product.objects.values_list('brand', flat=True).distinct()
    print("Unique Brands in user_home:", list(unique_brands))  # Debugging print
    categories = Category.objects.all()  # Fetch all categories from the database
    context = {
        'brands': unique_brands,
        'categories': categories,
    }
    return render(request, 'store/user_home.html', context)
  
# View for displaying products by category
def category_products(request, category):
    products = Product.objects.filter(name=category, cloth="mens")  # Adjust this to your filter logic
    return render(request, 'store/category_products.html', {'products': products, 'category': category})

def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/user_orders.html', {'orders': orders})

def order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return render(request, 'error.html', {'message': 'Order not found'})
    
    return render(request, 'orders/order_details.html', {'order': order})

# Display.html
def products_by_brand(request, brand):
    # Filter products by the selected brand
    products = Product.objects.filter(brand=brand)
    # Get all unique brand names for the dropdown
    unique_brands = Product.objects.values_list('brand', flat=True).distinct()
    context = {
        'products': products,
        'brand': brand,
        'brands': unique_brands,  # Pass the list of brands to the template
    }
    return render(request, 'store/display.html', context)

def products_by_category(request, category_name):
    # Filter the category based on the category_name
    category = Category.objects.get(name=category_name)
    # Filter products by the category
    products = Product.objects.filter(category=category)
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user_email=request.user.email).first()
        if wishlist:
            wishlist_ids = wishlist.item_ids
    # Pass the products and category to the template
    context = {
        'products': products,
        'category': category,
        'wishlist_ids': wishlist_ids,  # Pass the wishlist IDs
    }
    return render(request, 'store/display.html', context)

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    sizes = ProductSize.objects.filter(product=product)
    context = {
        'product': product,
        'sizes': sizes
    }
    return render(request, 'store/product_detail.html', context)

def search_products(request):
    search_query = request.GET.get('q', '')  # Get the search query from the URL
    products = Product.objects.filter(
        Q(name__icontains=search_query) | Q(description__icontains=search_query)
    )
    context = {
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'store/display.html', context)

def toggle_wishlist(request):
    if request.method == "GET":
        product_id = request.GET.get('product_id')
        if product_id:
            # Get the user's email as a string
            user_email = request.user.email

            # Retrieve or create the wishlist for the user
            wishlist, created = Wishlist.objects.get_or_create(user_email=user_email)

            # Toggle the product ID in the wishlist
            if product_id in wishlist.item_ids:
                wishlist.item_ids.remove(product_id)
            else:
                wishlist.item_ids.append(product_id)
            
            # Save the wishlist
            wishlist.save()

            return JsonResponse({'status': 'success', 'product_id': product_id})
    return JsonResponse({'status': 'error'})


def wishlist_view(request):
    if not request.user.is_authenticated:
        return render(request, 'store/error.html', {'message': 'You need to log in to view your wishlist'})

    user_email = request.user.email
    wishlist = Wishlist.objects.filter(user_email=user_email).first()

    if not wishlist or not wishlist.item_ids:
        return render(request, 'store/wishlist.html', {'products': []})

    # Get product details for the IDs in the wishlist
    products = Product.objects.filter(id__in=wishlist.item_ids)
    return render(request, 'store/wishlist.html', {'products': products})