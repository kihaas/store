from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from website.models import CartItem, Product
from website.extensions import db

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.json

    if not data or 'product_id' not in data:
        return jsonify({"error": "Необходимо указать product_id"}), 400

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "Количество должно быть положительным числом"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Товар не найден"}), 404

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Товар добавлен в корзину"}), 201


@cart_bp.route('/remove/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

    if not cart_item:
        return jsonify({"error": "Товар не найден в корзине"}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Товар удален из корзины"}), 200


@cart_bp.route('/update/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_cart(product_id):
    user_id = get_jwt_identity()
    data = request.json

    if not data or 'quantity' not in data:
        return jsonify({"error": "Необходимо указать quantity"}), 400

    quantity = data.get('quantity')
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "Количество должно быть положительным числом"}), 400

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Товар не найден в корзине"}), 404

    cart_item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Количество товара обновлено"}), 200


@cart_bp.route('/view', methods=['GET'])
@jwt_required()
def view_cart():
    user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    cart_data = []
    total_amount = 0

    for item in cart_items:
        product = Product.query.get(item.product_id)
        cart_data.append({
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": item.quantity,
            "total": product.price * item.quantity
        })
        total_amount += product.price * item.quantity

    return jsonify({"cart": cart_data, "total_amount": total_amount}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Корзина очищена"}), 200