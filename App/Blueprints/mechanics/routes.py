from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from App.models import Customer, Mechanic, db
from .schemas import mechanic_schema, mechanics_schema

mechanic_bp = Blueprint('mechanics_bp', __name__)  # Blueprint instance is named mechanic_bp

# Create mechanic
@mechanic_bp.route('', methods=['POST'])  
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    existing_email = db.session.execute(
        select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    ).scalars().first()
    if existing_email:
        return jsonify({"error": "Mechanic with this email already exists"}), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

 # Get all mechanics
@mechanic_bp.route('', methods=['GET'])
def get_mechanics():
    mechanics = db.session.execute(select(Mechanic)).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


# Get mechanic by ID
@mechanic_bp.route('/<int:mechanic_id>', methods=['GET'])
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
