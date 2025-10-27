from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from store.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name,
                'slug': product.slug,
                'image': product.main_image.url if product.main_image else '',
                'weight': product.weight,
                'weight_unit': product.weight_unit,
                'stock_quantity': product.stock_quantity,
                'added_at': timezone.now().isoformat()
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        # Ensure quantity doesn't exceed stock
        if self.cart[product_id]['quantity'] > product.stock_quantity:
            self.cart[product_id]['quantity'] = product.stock_quantity

        self.save()
        return True

    def save(self):
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update_quantity(self, product_id, quantity):
        """
        Update the quantity of a specific product.
        """
        if quantity <= 0:
            self.remove_by_id(product_id)
            return False

        if product_id in self.cart:
            # Get the product to check stock
            try:
                product = Product.objects.get(id=product_id)
                if quantity > product.stock_quantity:
                    quantity = product.stock_quantity

                self.cart[product_id]['quantity'] = quantity
                self.save()
                return True
            except Product.DoesNotExist:
                self.remove_by_id(product_id)
                return False
        return False

    def remove_by_id(self, product_id):
        """
        Remove a product by ID.
        """
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate the total cost of all items in the cart.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_items(self):
        """
        Get total number of items in the cart.
        """
        return len(self.cart)

    def get_cart_items(self):
        """
        Get cart items with product objects.
        """
        cart_items = []
        for item in self:
            cart_items.append(item)
        return cart_items

    def clear(self):
        """
        Remove cart from session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def is_empty(self):
        """
        Check if cart is empty.
        """
        return len(self.cart) == 0

    def get_summary(self):
        """
        Get cart summary for templates.
        """
        return {
            'total_items': len(self),
            'total_products': self.get_total_items(),
            'total_price': self.get_total_price(),
            'is_empty': self.is_empty()
        }