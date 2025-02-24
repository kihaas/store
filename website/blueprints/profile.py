from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from website.models import User, Order
from website import db
from website.forms import UpdateProfileForm

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    """
    Просмотр профиля пользователя.
    Требуется JWT-токен.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404

    return jsonify({
        'email': user.email,
        'login': user.login,
        'phone': user.phone
    })


@profile_bp.route('/profile/update', methods=['POST'])
@jwt_required()
def update_profile():
    """
    Обновление данных профиля пользователя.
    Требуется JWT-токен.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404

    form = UpdateProfileForm()

    if form.validate_on_submit():
        # Проверка уникальности email и логина
        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            return jsonify({'error': 'Email уже используется'}), 400

        if form.login.data != user.login and User.query.filter_by(login=form.login.data).first():
            return jsonify({'error': 'Логин уже используется'}), 400

        user.email = form.email.data
        user.login = form.login.data
        user.phone = form.phone.data

        if form.password.data:
            user.set_password(form.password.data)  # Хеширование пароля

        db.session.commit()

        # Генерация нового JWT-токена после обновления профиля
        new_token = create_access_token(identity=user.id)

        return jsonify({'message': 'Профиль успешно обновлён', 'new_token': new_token})

    return jsonify({'errors': form.errors}), 400


@profile_bp.route('/profile/orders', methods=['GET'])
@jwt_required()
def order_history():
    """
    Получение истории заказов пользователя.
    Требуется JWT-токен.
    """
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_id).all()

    orders_data = [
        {
            'order_id': order.id,
            'product_name': order.product_name,
            'quantity': order.quantity,
            'total_price': order.total_price,
            'status': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for order in orders
    ]

    return jsonify({'orders': orders_data})

'''from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "email": user.email,
        "phone": user.phone,
        "bonus_balance": user.bonus_balance
    }), 200'''