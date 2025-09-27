from .models import Category
from .cart import Cart

def categories(request):
    """
    Context processor to make categories available in all templates
    """
    return {
        'categories': Category.objects.filter(level=0, is_active=True)
    }

def cart(request):
    """
    Context processor to make cart available in all templates
    """
    return {
        'cart': Cart(request)
    }