import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = "supersecretkey"

def encode_token(user_id):
    payload= {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1),  # Token expires in 1 hour
        'iat': datetime.now(timezone.utc),  # Issued at time
        'sub': user_id  # Subject of the token, typically the user ID
    }
    
    token=jwt.encode(payload,SECRET_KEY,algorithm='HS256')
    return token