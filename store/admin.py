from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import pandas as pd
from django.utils.text import slugify
from mptt.admin import MPTTModelAdmin
from .models import Product, Category, ProductImage, ProductReview


class ProductImportExportAdmin(admin.ModelAdmin):
    change_list_template = "admin/store/product/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-products/', self.admin_site.admin_view(self.import_products), name='import_products'),
            path('export-products/', self.admin_site.admin_view(self.export_products), name='export_products'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='download_template'),
        ]
        return custom_urls + urls

    def import_products(self, request):
        if request.method == 'POST':
            file = request.FILES.get('file')
            file_format = request.POST.get('format', 'csv')

            if not file:
                messages.error(request, 'Please select a file to import.')
                return redirect('..')

            try:
                imported_count = 0
                error_count = 0
                errors = []

                if file_format == 'csv':
                    decoded_file = file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    for row_num, row in enumerate(reader, 2):  # Start from 2 (header is row 1)
                        success, message = self.create_product_from_row(row)
                        if success:
                            imported_count += 1
                        else:
                            error_count += 1
                            errors.append(f"Row {row_num}: {message}")

                elif file_format == 'excel':
                    df = pd.read_excel(file)
                    for index, row in df.iterrows():
                        success, message = self.create_product_from_row(row.to_dict())
                        if success:
                            imported_count += 1
                        else:
                            error_count += 1
                            errors.append(f"Row {index + 2}: {message}")

                if imported_count > 0:
                    messages.success(request, f'Successfully imported {imported_count} products.')
                if error_count > 0:
                    messages.warning(request, f'{error_count} products could not be imported.')
                    # Show first 5 errors
                    for error in errors[:5]:
                        messages.error(request, error)
                    if len(errors) > 5:
                        messages.error(request, f"... and {len(errors) - 5} more errors")

            except Exception as e:
                messages.error(request, f'Error importing products: {str(e)}')

            return redirect('..')

        return render(request, 'admin/store/product/import_products.html')

    def export_products(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'name', 'slug', 'description', 'price', 'wholesale_price',
            'category', 'product_type', 'brand', 'origin_country',
            'weight', 'stock_quantity', 'is_available', 'is_wholesale',
            'is_halal', 'is_vegetarian'
        ])

        products = Product.objects.all()
        for product in products:
            writer.writerow([
                product.name,
                product.slug,
                product.description,
                product.price,
                product.wholesale_price,
                product.category.name if product.category else '',
                product.product_type,
                product.brand,
                product.origin_country,
                product.weight,
                product.stock_quantity,
                product.is_available,
                product.is_wholesale,
                product.is_halal,
                product.is_vegetarian,
            ])

        return response

    def download_template(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_import_template.csv"'

        writer = csv.writer(response)

        # Header row
        writer.writerow([
            'name', 'slug', 'description', 'price', 'wholesale_price',
            'category', 'product_type', 'brand', 'origin_country',
            'weight', 'stock_quantity', 'is_available', 'is_wholesale',
            'is_halal', 'is_vegetarian'
        ])

        # Example rows with actual categories from your database
        categories = Category.objects.all()[:3]
        for i, category in enumerate(categories):
            writer.writerow([
                f'Example Product {i + 1}',
                f'example-product-{i + 1}',
                f'Description for example product {i + 1}',
                '10.99',
                '8.99',
                category.name,  # Use actual category name
                'grocery',
                'Example Brand',
                'India',
                '500g',
                '100',
                'True',
                'True',
                'True',
                'True'
            ])

        return response

    def create_product_from_row(self, data):
        try:
            # Required fields validation
            if not data.get('name') or not data.get('category'):
                return False, "Name and category are required"

            category_name = data.get('category', '').strip()
            category = Category.objects.filter(name__iexact=category_name).first()
            if not category:
                return False, f"Category '{category_name}' not found"

            # Generate slug if not provided
            slug = data.get('slug', '').strip()
            if not slug:
                slug = slugify(data['name'])

            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while Product.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            # Create product
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': data['name'].strip(),
                    'description': data.get('description', '').strip(),
                    'price': float(data.get('price', 0)),
                    'wholesale_price': float(data.get('wholesale_price', 0)) or None,
                    'category': category,
                    'product_type': data.get('product_type', 'grocery'),
                    'origin_country': data.get('origin_country', '').strip(),
                    'brand': data.get('brand', '').strip(),
                    'weight': data.get('weight', '').strip(),
                    'stock_quantity': int(data.get('stock_quantity', 0)),
                    'is_available': data.get('is_available', 'True').lower() == 'true',
                    'is_wholesale_available': data.get('is_wholesale', 'False').lower() == 'true',
                    'is_halal': data.get('is_halal', 'False').lower() == 'true',
                    'is_vegetarian': data.get('is_vegetarian', 'False').lower() == 'true',
                }
            )

            if created:
                return True, f"Created product: {product.name}"
            else:
                return False, f"Product already exists: {product.name}"

        except Exception as e:
            return False, f"Error: {str(e)}"


@admin.register(Product)
class ProductAdmin(ProductImportExportAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_quantity', 'is_available']
    list_filter = ['is_available', 'category', 'product_type', 'origin_country']
    search_fields = ['name', 'sku', 'brand']
    prepopulated_fields = {'slug': ('name',)}
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


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    mptt_level_indent = 20


# Register other models...
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_featured']
    list_filter = ['is_featured']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']