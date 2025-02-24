from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta

def generate_access_token(user_id):
    return create_access_token(identity=user_id, expires_delta=timedelta(hours=1))

def decode_access_token(token):
    return decode_token(token)