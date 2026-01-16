import os
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import request, jsonify

SECRET_KEY = os.environ.get("SECRET_KEY") or "super secret secrets"
ALGORITHM = "HS256"


def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token is missing!"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            data = decode_token(token)
            user_id = data.get("sub")
            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                return jsonify({"message": "Invalid token!"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(user_id, *args, **kwargs)

    return decorated


def encode_token(user_id):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        # Store subject as string because PyJWT validates `sub` must be a string
        "sub": str(user_id),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
