from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from App.models import Customer, Mechanic, db
from .schemas import mechanic_schema, mechanics_schema, login_schema
from App. extensions import cache
from App.utils.util import encode_token

mechanic_bp = Blueprint('mechanics_bp', __name__)  # Blueprint instance is named mechanic_bp

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
    mechanic_data = request.get_json()  # ✅ This makes mechanic_data a dictionary

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
@cache.cached(timeout=60)  # Cache the response for 60 seconds
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
