from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Auto-generate slug (e.g., "Smart Phone" -> "smart-phone")
            self.slug = self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    # Link Product to Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_names = models.TextField(default='')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a user can only save a specific product once
        unique_together = ('user', 'product')
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.user.username} saved {self.product.name}"
    
class Address(models.Model):
    """Stores shipping and billing addresses for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    
    # Address details
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=15)
    country = models.CharField(max_length=100, default='India')

    # Status fields
    is_default = models.BooleanField(default=False)
    address_type = models.CharField(max_length=20, choices=[('Shipping', 'Shipping'), ('Billing', 'Billing')], default='Shipping')

    def __str__(self):
        return f"{self.full_name} ({self.city})"

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', 'city']

class SavedCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_cards')
    card_number_last_four = models.CharField(max_length=4) # Only store last 4 digits
    card_holder_name = models.CharField(max_length=150)
    card_type = models.CharField(max_length=50) # e.g., Visa, Mastercard
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.card_type} **** {self.card_number_last_four}"

    class Meta:
        verbose_name_plural = "Saved Cards"

class SavedUPI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_upis')
    upi_id = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.upi_id

    class Meta:
        verbose_name_plural = "Saved UPI IDs"