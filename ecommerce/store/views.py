from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import Product, Category, TempUser , Order, ProductSize, Wishlist, Cart
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from .forms import RegisterForm, LoginForm 
import random, json
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q  
from datetime import datetime




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
            wishlist = Wishlist.objects.create(user_email= temp_user.email, item_ids=[])
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

    wishlist_items = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user_email=request.user.email).first()
        if wishlist:
            wishlist_items = wishlist.item_ids
    print("Wishlist items for user:", wishlist_items)  # Debugging print

    context = {
        'brands': unique_brands,
        'categories': categories,
        'wishlist_items': wishlist_items,  # Pass wishlist items to the template
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
    products = Product.objects.filter(brand=brand)
    all_brands = Product.objects.values_list('brand', flat=True).distinct()
    context = {
        'products': products,
        'brand': brand,
        'brands': all_brands,        # All brands for the dropdown
    }
    return render(request, 'store/display.html', context)

def products_by_category(request, category_name):
    # Get the selected category object
    category = Category.objects.get(name=category_name)

    # Filter products in this category
    products = Product.objects.filter(category=category)

    # Wishlist logic
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user_email=request.user.email).first()
        if wishlist:
            wishlist_ids = wishlist.item_ids

    # Get all unique brands for dropdown
    all_brands = Product.objects.values_list('brand', flat=True).distinct()

    # Get all categories for sidebar
    all_categories = Category.objects.all()

    # Pass everything to the template
    context = {
        'products': products,
        'category': category,
        'wishlist_ids': wishlist_ids,
        'brands': all_brands,
        'categories': all_categories,
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
    search_query = request.GET.get('q', '')
    selected_brand = request.GET.get('brand', '')
    selected_category = request.GET.get('category', '')
    selected_price = request.GET.get('price', '')

    # Start with all products matching the search query
    products = Product.objects.filter(
        Q(name__icontains=search_query) | Q(description__icontains=search_query)
    )

    # Apply brand filter if selected
    if selected_brand:
        products = products.filter(brand=selected_brand)

    # Apply category filter if selected
    if selected_category:
        products = products.filter(category__name=selected_category)

    # Apply price filter if selected
    if selected_price:
        try:
            max_price = float(selected_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass  # Ignore invalid input

    # Wishlist logic
    wishlist_items = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user_email=request.user.email).first()
        if wishlist:
            wishlist_items = wishlist.item_ids

    # Get all distinct brands and all categories
    brands = Product.objects.values_list('brand', flat=True).distinct()
    categories = Category.objects.all()

    context = {
        'products': products,
        'search_query': search_query,
        'wishlist_items': wishlist_items,
        'brands': brands,
        'categories': categories,
        'selected_brand': selected_brand,
        'selected_category': selected_category,
        'selected_price': selected_price,
    }

    return render(request, 'store/display.html', context)

def display_products(request):
    # Get all products
    products = Product.objects.all()

    # Get the user's wishlist
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user_email=request.user.email).first()
        wishlist_item_ids = wishlist.item_ids if wishlist else []
    else:
        wishlist_item_ids = []

    # Pass products and wishlist state to the template
    return render(request, 'store/display.html', {
        'products': products,
        'wishlist_item_ids': wishlist_item_ids
    })

def toggle_wishlist(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')

            # Get or create the wishlist for the user
            wishlist, created = Wishlist.objects.get_or_create(user_email=request.user.email)

            # Check if the product is already in the wishlist
            if product_id in wishlist.item_ids:
                wishlist.item_ids.remove(product_id)
                action = 'removed'
            else:
                wishlist.item_ids.append(product_id)
                action = 'added'

            # Save the updated wishlist
            wishlist.save()

            # Return the updated state
            return JsonResponse({
                'status': 'success',
                'action': action,
                'product_id': product_id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'User not authenticated or invalid request'})

def wishlist_view(request):
    user_email = request.user.email
    wishlist, created = Wishlist.objects.get_or_create(user_email=user_email)
    product_ids = wishlist.item_ids
    wishlist_items = Product.objects.filter(id__in=product_ids)
    brands = Product.objects.values_list('brand', flat=True).distinct()
    categories = Category.objects.all()
    context = {
        'wishlist_items': wishlist_items,
        'brands': brands,
        'categories': categories,
    }
    return render(request, 'store/wishlist.html', context)

def remove_from_wishlist(request, product_id):
    # Get the current user's email
    user_email = request.user.email
    
    # Get the wishlist for the current user by user_email
    wishlist = Wishlist.objects.get(user_email=user_email)
    
    # Get the product to be removed
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the product exists in the wishlist and remove it
    if product in wishlist.item_ids.all():  # 'item_ids' is a ManyToManyField
        wishlist.item_ids.remove(product)
    
    # Redirect to the wishlist page
    return redirect('wishlist')

# Move to cart
@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data['product_id']
            selected_size = data['size']

            # Check if product exists
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=400)

            # Check if selected size is available for the product
            if not selected_size:
                return JsonResponse({'status': 'error', 'message': 'Please select a size'}, status=400)

            # Add the product to the cart
            cart_item = Cart.objects.create(
                user_email=request.user.email,  # Adjust to get the user from the request as needed
                product=product,
                selected_size=selected_size,
                quantity=1,  # Adjust quantity as needed
                added_at=datetime.now()
            )

            return JsonResponse({'status': 'success', 'message': 'Item added to cart'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            # Log the exception for debugging purposes
            print(str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def view_cart(request):
    user_email = request.user.email
    cart_items = Cart.objects.filter(user_email=user_email)
    return render(request, 'store/cart.html', {'cart_items': cart_items})

def get_product_sizes(request, product_id):
    sizes = ProductSize.objects.filter(product_id=product_id)
    size_list = [size.size for size in sizes if size.stock > 0]  # Only available sizes
    return JsonResponse({"sizes": size_list})