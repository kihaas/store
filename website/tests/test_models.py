import pytest
from website.models import User, Product, CartItem, Order, BonusTransaction, Referral
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


def test_user_creation(app):
    with app.app_context():
        user = User(email="test@example.com", phone="+79123456789")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        assert User.query.filter_by(email="test@example.com").first() is not None


def test_product_creation(app):
    with app.app_context():
        product = Product(name="Test Product", price=100.0, stock=10)
        db.session.add(product)
        db.session.commit()
        assert Product.query.filter_by(name="Test Product").first() is not None