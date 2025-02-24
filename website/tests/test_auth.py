import pytest
from website import create_app
from website.models import User
from website.extensions import db

@pytest.fixture
def app():
    app = create_app(config_name='testing')
    db.init_app(app)  # Добавляем инициализацию
    with app.app_context():
        db.create_all()  # Создание таблиц
        yield app  # Возвращаем приложение
        db.session.remove()  # Чистим сессию после тестов
        db.drop_all()  # Удаляем таблицы


def test_register_user(app):
    client = app.test_client()
    response = client.post('/auth/register', json={
        "email": "test@example.com",
        "phone": "+79123456789",
        "password": "password123"
    })
    assert response.status_code == 201
    assert User.query.filter_by(email="test@example.com").first() is not None