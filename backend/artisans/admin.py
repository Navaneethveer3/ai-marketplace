from django.contrib import admin
from django.contrib import admin
from .models import Artisan, Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0

@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ("name", "craft_type")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "artisan", "price")

