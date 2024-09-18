<<<<<<< HEAD
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description')
    search_fields = ('category_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock_quantity', 'status')
    list_filter = ('category', 'sunlight_requirement', 'water_need', 'climate_compatibility')
    search_fields = ('product_name', 'description')
=======
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description')
    search_fields = ('category_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock_quantity', 'status')
    list_filter = ('category', 'sunlight_requirement', 'water_need', 'climate_compatibility')
    search_fields = ('product_name', 'description')
>>>>>>> origin/main
