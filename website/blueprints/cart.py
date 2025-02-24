from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from website.models import CartItem, Product
from website.extensions import db

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Товар не найден"}), 404
    cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": "Товар добавлен в корзину"}), 201
'''from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app import db
from app import Product  # Импортируем модели Product и Cart

cart_bp = Blueprint('cart', __name__)

# Маршрут для добавления товара в корзину
@cart_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required  # Только для авторизованных пользователей
def add_to_cart(product_id):
    """
    Добавляет товар в корзину пользователя.
    Проверка наличия товара в базе данных и его существования в корзине.
    """
    # Проверяем, существует ли товар в базе данных
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    # Проверяем, есть ли уже товар в корзине пользователя
    existing_cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing_cart_item:
        # Если товар уже есть в корзине, увеличиваем количество
        existing_cart_item.quantity += 1
        db.session.commit()
        return jsonify({"message": "Product quantity updated in cart"})
    
    # Если товара нет в корзине, создаём новый объект Cart и добавляем его
    new_cart_item = Cart(user_id=current_user.id, product_id=product.id, quantity=1)
    db.session.add(new_cart_item)
    db.session.commit()

    return jsonify({"message": "Product added to cart"}), 200

# Маршрут для просмотра корзины
@cart_bp.route('/view_cart', methods=['GET'])
@login_required  # Только для авторизованных пользователей
def view_cart():
    """
    Отображает все товары в корзине пользователя, включая их количество.
    """
    # Получаем все товары в корзине для текущего пользователя
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({"message": "Your cart is empty"}), 200
    
    # Составляем список товаров с их количеством
    cart_details = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        cart_details.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "price": product.price,
            "total_price": product.price * item.quantity
        })

    return jsonify({"cart_items": cart_details}), 200

# Маршрут для удаления товара из корзины
@cart_bp.route('/remove_from_cart/<int:product_id>', methods=['DELETE'])
@login_required  # Только для авторизованных пользователей
def remove_from_cart(product_id):
    """
    Удаляет товар из корзины пользователя по ID.
    """
    # Находим товар в корзине
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if not cart_item:
        return jsonify({"message": "Product not in cart"}), 404
    
    # Удаляем товар из корзины
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({"message": "Product removed from cart"}), 200

# Маршрут для подсчета общей суммы заказа в корзине
@cart_bp.route('/total_price', methods=['GET'])
@login_required  # Только для авторизованных пользователей
def total_price():
    """
    Рассчитывает общую сумму товаров в корзине.
    """
    # Получаем все товары в корзине для текущего пользователя
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({"message": "Your cart is empty"}), 200
    
    total = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        total += product.price * item.quantity

    return jsonify({"total_price": total}), 200'''

'''from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.token_utils import generate_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user, error = AuthService.register_user(data.get('email'), data.get('phone'), data.get('password'), data.get('referral_code'))
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Пользователь зарегистрирован", "user_id": user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user, error = AuthService.login_user(data.get('email'), data.get('password'))
    if error:
        return jsonify({"error": error}), 401
    access_token = generate_access_token(user.id)
    return jsonify({"access_token": access_token}), 200'''