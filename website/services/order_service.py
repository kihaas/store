from website.models import Order, CartItem, Product
from website.extensions import db


class OrderService:
    @staticmethod
    def create_order(user_id):
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return None, "Корзина пуста"

        # Проверка наличия товаров на складе
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product.stock < item.quantity:
                return None, f"Недостаточно товара на складе: {product.name}"

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        order = Order(user_id=user_id, total_amount=total_amount)
        db.session.add(order)

        # Уменьшение количества товаров на складе
        for item in cart_items:
            product = Product.query.get(item.product_id)
            product.stock -= item.quantity

        db.session.commit()
        return order, None