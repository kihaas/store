from flask_mail import Message
from website.extensions import mail
from website.models import User
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def send_password_reset_email(user):

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='password-reset')
    reset_url = f"http://127.0.0.1:5000/reset_password?token={token}"

    msg = Message(
        subject="Восстановление пароля",
        recipients=[user.email],
        body=f"Для восстановления пароля перейдите по ссылке: {reset_url}"
    )
    mail.send(msg)