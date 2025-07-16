import jwt
from datetime import datetime, timezone, timedelta
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify


SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise ValueError("Invalid token") from e

    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if the token is provided in the request headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['sub']  # Fetch the user ID
            
        except jose.exceptions.ExpiredSignatureError:
             return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
             return jsonify({'message': 'Invalid token!'}), 401

        return f(user_id, *args, **kwargs)

    return decorated

def encode_token(user_id):
    payload= {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1),  # Token expires in 1 hour
        'iat': datetime.now(timezone.utc),  # Issued at time
        'sub': user_id  # Subject of the token, typically the user ID
    }
    
    token=jwt.encode(payload,SECRET_KEY,algorithm='HS256')
    return token