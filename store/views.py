from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Category, Product

def home(request):
    """Home page view"""
    # For now, just return a simple response
    return HttpResponse("""
    <h1>Welcome to Sunrise Supermarkt</h1>
    <p>South Asian, Asian, African & Oriental Groceries</p>
    <a href="/admin/">Admin Panel</a> | 
    <a href="/products/">Products</a>
    """)

def product_list(request):
    """Product list view"""
    products = Product.objects.filter(is_available=True)
    return HttpResponse(f"""
    <h1>Products</h1>
    <p>Total products: {products.count()}</p>
    <a href="/">Home</a>
    """)

def category_products(request, slug):
    """Category products view"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)
    return HttpResponse(f"""
    <h1>Category: {category.name}</h1>
    <p>Products in this category: {products.count()}</p>
    <a href="/products/">All Products</a> | 
    <a href="/">Home</a>
    """)

def product_detail(request, slug):
    """Product detail view"""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    return HttpResponse(f"""
    <h1>{product.name}</h1>
    <p>Price: ${product.price}</p>
    <p>{product.description}</p>
    <a href="/products/">Back to Products</a>
    """)