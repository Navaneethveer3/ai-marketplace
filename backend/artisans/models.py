from django.db import models
from django.contrib.auth.models import User


class Artisan(models.Model):
    name = models.CharField(max_length=120)
    craft_type = models.CharField(max_length=80)
    story = models.TextField(blank=True)
    image = models.ImageField(upload_to="artisans/", null=True, blank=True)
    ai_tagline = models.CharField(max_length=200, blank=True)  # will be filled by AI

    def __str__(self):
        return f"{self.name} - {self.craft_type}"

class Product(models.Model):
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    ai_description = models.TextField(blank=True)  # filled by AI

    def __str__(self):
        return f"{self.name} ({self.artisan.name})"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"