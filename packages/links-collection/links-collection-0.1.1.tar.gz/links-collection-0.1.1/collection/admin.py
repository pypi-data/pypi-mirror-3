from django.contrib import admin

from .models import Category, Product, Photo


class PhotoInline(admin.TabularInline):
    model = Photo


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        PhotoInline,
    ]

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Photo)
