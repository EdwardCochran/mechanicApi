from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from App.models import Customer, Mechanic, db, service_mechanic
from .schemas import mechanic_schema, mechanics_schema, login_schema
from App.extensions import cache
from App.utils.util import encode_token
from functools import wraps
from flask import request, jsonify
from App.utils.util import decode_token  

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401

        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            customer_id = payload.get("sub")
            if not customer_id:
                raise ValueError("Invalid token")
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(customer_id, *args, **kwargs)
    return decorated

mechanic_bp = Blueprint('mechanics_bp', __name__) 

@mechanic_bp.route("/login", methods=['POST'])
def login_mechanic():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == email, Mechanic.password == password)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic:
        token = encode_token(mechanic.id)
        response = {
            "status": "success",
            "message": "Login successful",
            "token": token,
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401





# Create mechanic
@mechanic_bp.route('', methods=['POST'])
def create_mechanic():
    mechanic_data = request.get_json()  
    phone = mechanic_data.get('phone', '')
    if not (isinstance(phone, str) and phone.isdigit() and len(phone) == 10):
        return jsonify({"error": "Phone must be exactly 10 digits"}), 400

    # Check for existing phone or email
    existing = db.session.execute(
        select(Mechanic).where(
            (Mechanic.email == mechanic_data['email']) |
            (Mechanic.phone == mechanic_data['phone'])
        )
    ).scalars().first()

    if existing:
        return jsonify({"error": "Mechanic with this email or phone already exists"}), 400

    # Create new mechanic
    new_mechanic = Mechanic(
        name=mechanic_data['name'],
        email=mechanic_data['email'],
        password=mechanic_data['password'],
        phone=mechanic_data['phone'],
        salary=mechanic_data['salary']
    )

    db.session.add(new_mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic created"}), 201

 # Get all mechanics
@mechanic_bp.route('', methods=['GET'])
def get_mechanics():
    mechanics = db.session.execute(select(Mechanic)).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


# Get mechanic by ID
@mechanic_bp.route('/<int:mechanic_id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache to speed up request for the same mechanic
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    return mechanic_schema.jsonify(mechanic), 200

# Update mechanic

@mechanic_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    mechanic_data = request.json 
    if 'phone' in mechanic_data:
        phone = mechanic_data.get('phone', '')
        if not (isinstance(phone, str) and phone.isdigit() and len(phone) == 10):
            return jsonify({"error": "Phone must be exactly 10 digits"}), 400

    for key, value in mechanic_data.items():
        if hasattr(mechanic, key):
            setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# Delete mechanic
@mechanic_bp.route('/<int:mechanic_id>', methods=['DELETE'])

def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic id: {mechanic_id} successfully deleted."}), 200


@mechanic_bp.route('/top-by-tickets', methods=['GET'])
def mechanics_by_ticket_count():
    counts = (
        db.session.query(
            Mechanic,
            db.func.count(service_mechanic.c.ticket_id).label("ticket_count"),
        )
        .outerjoin(service_mechanic, Mechanic.id == service_mechanic.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(db.desc("ticket_count"))
        .all()
    )

    mechanics = [
        {**mechanic_schema.dump(mechanic), "ticket_count": ticket_count}
        for mechanic, ticket_count in counts
    ]
    return jsonify(mechanics), 200
