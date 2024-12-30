from django.db import models

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