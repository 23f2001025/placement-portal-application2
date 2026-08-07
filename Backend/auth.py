import jwt
from datetime import datetime, timedelta
from flask import current_app

def create_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")

from functools import wraps
from flask import request, jsonify

def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"success": False, "message": "Missing token"}), 401

            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify({"success": False, "message": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"success": False, "message": "Invalid token"}), 401

            if payload["role"] != role:
                return jsonify({"success": False, "message": "Unauthorized"}), 403

            request.user_id = payload["user_id"]   
            request.user_role = payload["role"]
            return f(*args, **kwargs)
        return wrapper
    return decorator