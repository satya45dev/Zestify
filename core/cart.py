from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart and remove 'ghost' items."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        
        # --- NEW AUTO-CLEANUP LOGIC ---
        # This runs every time the cart is used
        self.cleanup_ghost_items()

    def cleanup_ghost_items(self):
        """Remove items from session that don't exist in the database."""
        product_ids = list(self.cart.keys())
        
        # Find which of these IDs actually exist in the DB
        valid_products = Product.objects.filter(id__in=product_ids).values_list('id', flat=True)
        valid_ids = [str(pid) for pid in valid_products]
        
        cart_modified = False
        for pid in product_ids:
            if pid not in valid_ids:
                # If session ID is not in DB, remove it
                del self.cart[pid]
                cart_modified = True
        
        if cart_modified:
            self.save()

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total = Decimal('0.00')
        
        for product in products:
            cart_item = self.cart.get(str(product.id))
            if cart_item:
                total += Decimal(cart_item['price']) * cart_item['quantity']
        return total

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True