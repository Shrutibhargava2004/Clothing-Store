from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import Product, Category
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm 

# Home page view
def home(request):
    return render(request, 'store/home.html')

# Login view (fixed for email authentication)
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate using email (adjust authenticate method)
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "You are now logged in!")
                    return redirect('user_home')  # Redirect to the user home or dashboard
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
        form = RegisterForm(request.POST)  # Initialize the form with POST data
        if form.is_valid():
            # Extract cleaned data from form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()  # Save the new user to the database

            # Flash success message
            messages.success(request, "Registration successful! Please log in.")

            # Redirect to the login page
            return redirect('login')
        else:
            # If form is invalid, display error messages
            messages.error(request, "There was an error with your registration. Please check the details.")
    else:
        # Display empty form on GET request
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')  # Redirect to home or login page after logout

def user_home(request):
    categories = Category.objects.all()
    print(categories)  # Debug line to check if categories are being fetched correctly
    return render(request, 'store/user_home.html', {'categories': categories})
        
def user_navbar(request):
    return redirect('user_navbar')
    
# View for displaying products by category
def category_products(request, category):
    products = Product.objects.filter(name=category, cloth="mens")  # Adjust this to your filter logic
    return render(request, 'store/category_products.html', {'products': products, 'category': category})