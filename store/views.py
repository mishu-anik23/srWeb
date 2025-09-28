from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product, ProductImage
from django.core.paginator import Paginator


def home(request):
    """Home page with featured products and categories"""
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    bestseller_products = Product.objects.filter(is_bestseller=True, is_available=True)[:8]
    categories = Category.objects.filter(level=0, is_active=True)

    context = {
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """All products listing with filtering and pagination"""
    products = Product.objects.filter(is_available=True)

    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category__in=category.get_descendants(include_self=True))

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sort by
    sort_by = request.GET.get('sort_by', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.filter(level=0, is_active=True),
        'total_products': products.count(),
    }
    return render(request, 'store/product_list.html', context)


def category_products(request, slug):
    """Products by category"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category__in=category.get_descendants(include_self=True),
        is_available=True
    )

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'subcategories': category.get_children(),
        'categories': Category.objects.filter(level=0, is_active=True),
    }
    return render(request, 'store/category_products.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    # Get all images for the product
    product_images = product.images.all()

    context = {
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)