import pytest
from website.models import User, Product, CartItem, Order, BonusTransaction
from website.services.auth_service import AuthService
from website.services.bonus_service import BonusService
from website.services.order_service import OrderService
from website.extensions import db


@pytest.fixture
def app():
    from website import create_app
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_auth_service_register_user(app):
    """
    Тестирование регистрации пользователя через AuthService.
    """
    with app.app_context():
        # Регистрация нового пользователя
        user, error = AuthService.register_user(
            email="test@example.com",
            phone="+79123456789",
            password="password123"
        )
        assert user is not None
        assert error is None

        # Проверка, что пользователь сохранен в базе данных
        db_user = User.query.filter_by(email="test@example.com").first()
        assert db_user is not None
        assert db_user.phone == "+79123456789"


def test_auth_service_login_user(app):
    """
    Тестирование входа пользователя через AuthService.
    """
    with app.app_context():
        # Создаем пользователя
        user = User(email="test@example.com", phone="+79123456789")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Успешный вход
        logged_in_user, error = AuthService.login_user("test@example.com", "password123")
        assert logged_in_user is not None
        assert error is None

        # Неверный пароль
        logged_in_user, error = AuthService.login_user("test@example.com", "wrong_password")
        assert logged_in_user is None
        assert error == "Неверные данные для входа"


def test_bonus_service_add_bonus(app):
    """
    Тестирование начисления и списания бонусов через BonusService.
    """
    with app.app_context():
        # Создаем пользователя
        user = User(email="test@example.com", phone="+79123456789")
        db.session.add(user)
        db.session.commit()

        # Начисление бонусов
        bonus_transaction, error = BonusService.add_bonus(user.id, 100.0, "credit")
        assert bonus_transaction is not None
        assert error is None
        assert user.bonus_balance == 100.0

        # Списание бонусов
        bonus_transaction, error = BonusService.add_bonus(user.id, 50.0, "debit")
        assert bonus_transaction is not None
        assert error is None
        assert user.bonus_balance == 50.0

        # Попытка списать больше бонусов, чем есть
        bonus_transaction, error = BonusService.add_bonus(user.id, 100.0, "debit")
        assert bonus_transaction is None
        assert error == "Недостаточно бонусов"


def test_order_service_create_order(app):
    """
    Тестирование создания заказа через OrderService.
    """
    with app.app_context():
        # Создаем пользователя и товар
        user = User(email="test@example.com", phone="+79123456789")
        product = Product(name="Test Product", price=100.0, stock=10)
        db.session.add(user)
        db.session.add(product)
        db.session.commit()

        # Добавляем товар в корзину
        cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        # Создаем заказ
        order, error = OrderService.create_order(user.id)
        assert order is not None
        assert error is None
        assert order.total_amount == 200.0  # 2 товара по 100 рублей

        # Проверяем, что количество товара на складе уменьшилось
        updated_product = Product.query.get(product.id)
        assert updated_product.stock == 8

        # Попытка создать заказ с пустой корзиной
        CartItem.query.delete()
        db.session.commit()
        order, error = OrderService.create_order(user.id)
        assert order is None
        assert error == "Корзина пуста"


def test_order_service_insufficient_stock(app):
    """
    Тестирование создания заказа при недостаточном количестве товара на складе.
    """
    with app.app_context():
        # Создаем пользователя и товар
        user = User(email="test@example.com", phone="+79123456789")
        product = Product(name="Test Product", price=100.0, stock=1)
        db.session.add(user)
        db.session.add(product)
        db.session.commit()

        # Добавляем товар в корзину (количество больше, чем на складе)
        cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        # Попытка создать заказ
        order, error = OrderService.create_order(user.id)
        assert order is None
        assert error == "Недостаточно товара на складе: Test Product"