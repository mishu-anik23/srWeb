from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Product
from .cart import Cart


def cart_detail(request):
    """
    Display the shopping cart.
    """
    cart = Cart(request)
    return render(request, 'store/cart/cart_detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_available=True)

    quantity = int(request.POST.get('quantity', 1))

    # Check stock availability
    if quantity > product.stock_quantity:
        messages.error(request, f"Only {product.stock_quantity} units available in stock.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f"Only {product.stock_quantity} units available in stock."
            })
        return redirect('store:product_detail', slug=product.slug)

    cart.add(product, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart successfully!',
            'cart_summary': cart.get_summary()
        })

    messages.success(request, f"{product.name} added to your cart.")
    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Product removed from cart.',
            'cart_summary': cart.get_summary()
        })

    messages.success(request, "Product removed from your cart.")
    return redirect('store:cart_detail')


@require_POST
def cart_update(request, product_id):
    """
    Update product quantity in the cart.
    """
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))

    success = cart.update_quantity(str(product_id), quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Cart updated successfully!',
                'cart_summary': cart.get_summary()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to update cart.'
            })

    if success:
        messages.success(request, "Cart updated successfully!")
    else:
        messages.error(request, "Failed to update cart.")

    return redirect('store:cart_detail')


def cart_summary(request):
    """
    Get cart summary for AJAX requests.
    """
    cart = Cart(request)
    return JsonResponse(cart.get_summary())