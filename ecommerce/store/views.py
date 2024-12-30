from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import Product, Category, TempUser 
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm 
import random
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


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

@login_required
def user_home(request):
    return render(request, 'store/user_home.html')

def user_navbar(request):
    return redirect('user_navbar')
    
# View for displaying products by category
def category_products(request, category):
    products = Product.objects.filter(name=category, cloth="mens")  # Adjust this to your filter logic
    return render(request, 'store/category_products.html', {'products': products, 'category': category})