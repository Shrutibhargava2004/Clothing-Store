from django.contrib import admin
from .models import Category,TempUser, Product, Order, OrderItem, Payment,ProductSize, Wishlist
from django.http import HttpResponseRedirect
from django.urls import reverse

# Register the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)

# Register the Product model
# Inline model admin to display ProductSize as part of Product
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1  # Number of empty forms to show (default is 3)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'category')  # Display these columns in the list view
    search_fields = ('name', 'brand')  # Enable search functionality by product name and brand
    inlines = [ProductSizeInline]  # Add ProductSize as inline inside the Product form

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductSize)  

admin.site.register(TempUser)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty order item forms to show by default

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'status', 'total_price', 'shipping_address', 'shipping_date')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]
    
    # Make the shipping_date editable in the admin form
    fields = ('user', 'order_date', 'status', 'total_price', 'shipping_address', 'shipping_date')
    
    actions = ['mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, "Selected orders marked as shipped.")
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, "Selected orders marked as delivered.")
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, "Selected orders marked as cancelled.")
    
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'payment_status', 'amount', 'payment_date')
    search_fields = ('order__id', 'transaction_id')
    
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'item_ids')  # Change 'user' to 'user_email'
    # You can add other configurations here if needed

admin.site.register(Wishlist, WishlistAdmin)