from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products_by_category', args=[self.slug])


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('grocery', 'Grocery'),
        ('fruit', 'Exotic Fruits'),
        ('vegetable', 'Fresh Vegetables'),
        ('frozen', 'Frozen Foods'),
        ('spice', 'Spices'),
        ('beverage', 'Beverages'),
        ('snack', 'Snacks'),
        ('ready_to_eat', 'Ready to Eat'),
        ('personal_care', 'Personal Care'),
        ('home_care', 'Home Care'),
    ]

    WEIGHT_UNIT_CHOICES = [
        ('g', 'Gram'),
        ('kg', 'Kilogram'),
        ('ml', 'Milliliter'),
        ('l', 'Liter'),
        ('pcs', 'Pieces'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    category = TreeForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_wholesale_available = models.BooleanField(default=False)
    wholesale_min_quantity = models.IntegerField(default=10)

    # Inventory
    sku = models.CharField(max_length=50, unique=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(max_length=5, choices=WEIGHT_UNIT_CHOICES, blank=True)

    # Product Details
    brand = models.CharField(max_length=100, blank=True)
    origin_country = models.CharField(max_length=100)
    is_halal = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    expiry_date = models.DateField(blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True)

    # Status
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)

    # Images
    main_image = models.ImageField(upload_to='products/main/')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f"{self.name} - {self.brand}" if self.brand else self.name

    def save(self, *args, **kwargs):
        if not self.sku:
            # Generate SKU automatically
            base_sku = f"{self.category.name[:3].upper()}{self.name[:3].upper()}"
            counter = 1
            self.sku = f"{base_sku}{counter:03d}"
            while Product.objects.filter(sku=self.sku).exists():
                counter += 1
                self.sku = f"{base_sku}{counter:03d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
