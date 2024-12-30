from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CLOTH_CHOICES = [
        ('kids', 'Kids'),
        ('men', 'Men'),
        ('women', 'Women'),
    ]

    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]

    # Define the model fields
    id = models.AutoField(primary_key=True)  # Auto incrementing id
    brand = models.CharField(max_length=255)
    cloth = models.CharField(max_length=5, choices=CLOTH_CHOICES)  # 'kids', 'men', 'women'
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    size = models.CharField(max_length=3, choices=SIZE_CHOICES)  # Size options (S, M, L, etc.)

    def __str__(self):
        return f"{self.name} ({self.brand})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

class TempUser(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username

# class OTP(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
#     otp = models.CharField(max_length=6)
#     email = models.EmailField()  # or other fields, depending on your model
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"OTP for {self.email}"