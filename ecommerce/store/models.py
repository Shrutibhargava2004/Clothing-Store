from django.db import models
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import ArrayField  # For list field

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

class Product(models.Model):
    # Define the model fields
    id = models.AutoField(primary_key=True)  # Auto incrementing id
    brand = models.CharField(max_length=255)
    cloth = models.CharField(choices=[('kids', 'Kids'), ('men', 'Men'), ('women', 'Women')], max_length=5)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    # stock = models.IntegerField()
    # size = models.CharField(choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large'), ('XXL', 'Double Extra Large')], max_length=3)
    image = models.ImageField(upload_to='products/')
    # Add foreign key to Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    # wishlist_users = models.ManyToManyField(User, related_name='wishlist_products', blank=True)

    def __str__(self):
        return f"{self.name} ({self.brand})"

class ProductSize(models.Model):
    # The ProductSize model will store size and stock for each size of a product
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large'), ('XXL', 'Double Extra Large')], max_length=3)
    stock = models.IntegerField(default=0)  # Stock quantity for this particular size

    def __str__(self):
        return f"{self.product.name} - {self.size}"

        
class Wishlist(models.Model):
    user_email = models.EmailField(unique=True)
    item_ids = models.JSONField(default=list)  # or use a ManyToManyField for products

    def __str__(self):
        return f"{self.user_email}"

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


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Customer who placed the order
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    shipping_date = models.DateField(null=True, blank=True)  # New field for the shipping date

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} ({self.status})"

    def update_total_price(self):
        # Calculate total price for the order based on the order items
        order_items = OrderItem.objects.filter(order=self)
        self.total_price = sum(item.total_price() for item in order_items)
        self.save()

    def get_items(self):
        return OrderItem.objects.filter(order=self)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.payment_status}"

class Cart(models.Model):
    user_email = models.EmailField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    selected_size = models.CharField(max_length=5)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} ({self.selected_size}) - {self.user_email}"