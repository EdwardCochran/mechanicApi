from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from App.models import Customer, Mechanic, db
from .schemas import mechanic_schema, mechanics_schema
from . import mechanics_bp



# Create mechanic
@mechanics_bp.route('', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check for existing email
    existing_email = db.session.execute(
        select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    ).scalars().first()
    if existing_email:
        return jsonify({"error": "Mechanic with this email already exists"}), 400

    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201
