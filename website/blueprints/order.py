import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from website.models import Order, CartItem, User
from website.extensions import db
import requests
from datetime import datetime


order_bp = Blueprint('order', __name__)


YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
YOOKASSA_API_URL = 'https://api.yookassa.ru/v3/payments'


@order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Корзина пуста"}), 400

    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    order = Order(user_id=user_id, total_amount=total_amount)
    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "Заказ создан", "order_id": order.id}), 201


@order_bp.route('/generate_payment_link/<int:order_id>', methods=['POST'])
@jwt_required()
def generate_payment_link(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == "Оплачен":
        return jsonify({"error": "Заказ уже оплачен"}), 400

    payment_data = {
        "amount": {"value": str(order.total_amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "http://your-website.com/payment_success"},
        "description": f"Оплата заказа #{order.id}"
    }

    auth = (YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)
    response = requests.post(YOOKASSA_API_URL, json=payment_data, auth=auth)

    if response.status_code == 200:
        payment_info = response.json()
        order.payment_id = payment_info['id']
        order.payment_link = payment_info['confirmation']['confirmation_url']
        db.session.commit()
        return jsonify({"payment_link": order.payment_link}), 200

    return jsonify({"error": "Не удалось создать ссылку на оплату"}), 500


@order_bp.route('/yookassa_webhook', methods=['POST'])
def yookassa_webhook():
    data = request.json
    payment_id = data['object']['id']
    order = Order.query.filter_by(payment_id=payment_id).first()

    if order and data['object']['status'] == 'succeeded':
        order.status = "Оплачен"
        db.session.commit()
        return jsonify({"status": "ok"}), 200

    return jsonify({"error": "Неверные данные"}), 400