from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'review_date')
    search_fields = ('user__fname', 'product__name')
    list_filter = ('rating',)
