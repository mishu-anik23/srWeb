from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Product, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    mptt_level_indent = 20


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_quantity', 'is_available']
    list_filter = ['is_available', 'category', 'product_type', 'origin_country']
    search_fields = ['name', 'sku', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'product_type')
        }),
        ('Pricing', {
            'fields': ('price', 'wholesale_price', 'cost_price', 'is_wholesale_available', 'wholesale_min_quantity')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'low_stock_threshold', 'weight', 'weight_unit')
        }),
        ('Product Details', {
            'fields': ('brand', 'origin_country', 'is_halal', 'is_vegetarian', 'expiry_date', 'batch_number')
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured', 'is_bestseller', 'main_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title']