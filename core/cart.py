from products.models import Product

from cart.models import CartItem


class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.user = getattr(request, "user", None)
        self.use_db = bool(self.user and self.user.is_authenticated)
        self._items_cache = None

        if self.use_db:
            self.cart = None
            self._merge_session_cart()
        else:
            cart = self.session.get('cart')
            if not cart:
                cart = self.session['cart'] = {}
            self.cart = cart

    def add(self, product, quantity=1):
        product_id = self._get_product_id(product)

        if self.use_db:
            self._db_add(product_id, quantity)
            return

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}

        self.cart[product_id]['quantity'] += quantity
        self.save()

    def decrease(self, product):
        product_id = self._get_product_id(product)

        if self.use_db:
            item = CartItem.objects.filter(user=self.user, product_id=product_id).first()
            if not item:
                return
            item.quantity -= 1
            if item.quantity <= 0:
                item.delete()
            else:
                item.save()
            self._items_cache = None
            return

        if product_id in self.cart:
            self.cart[product_id]['quantity'] -= 1

            if self.cart[product_id]['quantity'] <= 0:
                del self.cart[product_id]

        self.save()

    def remove(self, product):
        product_id = self._get_product_id(product)

        if self.use_db:
            CartItem.objects.filter(user=self.user, product_id=product_id).delete()
            self._items_cache = None
            return

        if product_id in self.cart:
            del self.cart[product_id]

        self.save()

    def clear(self):
        if self.use_db:
            CartItem.objects.filter(user=self.user).delete()
            self._items_cache = None
            return

        self.session.pop("cart", None)
        self.cart = {}
        self.save()

    def save(self):
        if not self.use_db:
            self.session.modified = True

    def __iter__(self):
        if self.use_db:
            for item in self._get_db_items():
                yield {
                    "product": item.product,
                    "quantity": item.quantity,
                    "total_price": item.product.price * item.quantity,
                }
            return

        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            item = self.cart[str(product.id)]
            item['product'] = product
            item['total_price'] = product.price * item['quantity']
            yield item

    def get_total_price(self):
        if self.use_db:
            return sum(item.product.price * item.quantity for item in self._get_db_items())

        return sum(
            item['product'].price * item['quantity']
            for item in self
        )

    def get_total_quantity(self):
        if self.use_db:
            return sum(item.quantity for item in self._get_db_items())

        return sum(item['quantity'] for item in self.cart.values())

    def get_products(self):
        if self.use_db:
            product_ids = [item.product_id for item in self._get_db_items()]
            return Product.objects.filter(id__in=product_ids)
        product_ids = self.cart.keys()
        return Product.objects.filter(id__in=product_ids)

    def _get_product_id(self, product):
        if isinstance(product, Product):
            return str(product.id)
        return str(product)

    def _get_db_items(self):
        if self._items_cache is None:
            self._items_cache = list(
                CartItem.objects.filter(user=self.user).select_related("product")
            )
        return self._items_cache

    def _db_add(self, product_id, quantity):
        if quantity <= 0:
            return
        item, _ = CartItem.objects.get_or_create(
            user=self.user,
            product_id=product_id,
            defaults={"quantity": 0},
        )
        item.quantity += quantity
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
        self._items_cache = None

    def _merge_session_cart(self):
        cart = self.session.get("cart")
        if not isinstance(cart, dict) or not cart:
            return
        for product_id, payload in cart.items():
            try:
                quantity = int(payload.get("quantity", 0))
            except (TypeError, ValueError):
                continue
            if quantity > 0:
                self._db_add(product_id, quantity)
        try:
            del self.session["cart"]
        except KeyError:
            pass
        self.session.modified = True
