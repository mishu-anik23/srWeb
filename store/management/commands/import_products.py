import csv
import pandas as pd
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from store.models import Product, Category


class Command(BaseCommand):
    help = 'Import products from CSV or Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV or Excel file')
        parser.add_argument('--format', type=str, default='csv', choices=['csv', 'excel'], help='File format')

    def handle(self, *args, **options):
        file_path = options['file_path']
        file_format = options['format']

        try:
            if file_format == 'csv':
                products_created = self.import_from_csv(file_path)
            else:
                products_created = self.import_from_excel(file_path)

            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {products_created} products')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing products: {str(e)}')
            )

    def import_from_csv(self, file_path):
        products_created = 0
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if self.create_product(row):
                    products_created += 1
        return products_created

    def import_from_excel(self, file_path):
        products_created = 0
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            if self.create_product(row.to_dict()):
                products_created += 1
        return products_created

    def create_product(self, data):
        try:
            # Get or create category
            category_name = data.get('category', '').strip()
            if not category_name:
                self.stdout.write(self.style.WARNING('Skipping product - no category specified'))
                return False

            category = Category.objects.filter(name__iexact=category_name).first()
            if not category:
                self.stdout.write(self.style.WARNING(f'Category not found: {category_name}'))
                return False

            # Create product
            product, created = Product.objects.get_or_create(
                name=data['name'].strip(),
                defaults={
                    'slug': data.get('slug', '').strip() or self.generate_slug(data['name']),
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
                    'is_wholesale': data.get('is_wholesale', 'False').lower() == 'true',
                    'is_halal': data.get('is_halal', 'False').lower() == 'true',
                    'is_vegetarian': data.get('is_vegetarian', 'False').lower() == 'true',
                }
            )

            if created:
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')

            return created

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating product {data.get("name", "Unknown")}: {str(e)}'))
            return False

    def generate_slug(self, name):
        from django.utils.text import slugify
        return slugify(name)