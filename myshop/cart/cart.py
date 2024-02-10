from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart:
    def __init__(self, request):    # метод класса, который инициализирует созданный объект.
        self.session = request.session  # Текущий сеанс сохраняется посредством этой инструкции
        cart = self.session.get(settings.CART_SESSION_ID)   # запрос корзины из текущего сеанса
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}  # сохранить пустую корзину в сеансе если в сеансе ее нет
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Добавить товар в количестве либо обновить его количество.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True    # сохранение измененного сеанса

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]   # удаление из словаря строки
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()  # получение продуктов из корзины методом по ключу
        products = Product.objects.filter(id__in=product_ids)   # получить продукт и добавить в корзину
        cart = self.cart.copy()     # текущая корзина копируется в эту переменную
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()