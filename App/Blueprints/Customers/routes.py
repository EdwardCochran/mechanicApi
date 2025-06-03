from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from App.models import Customer, db
from .schemas import customer_schema, customers_schema
from . import customers_bp

# Blueprint setup
# customers_bp = Blueprint('customer_bp', __name__)

# Schema instances
# customer_schema = CustomerSchema()
# customers_schema = CustomersSchema(many=True)

# Create customer
@customers_bp.route('', methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check for existing email
    existing_email = db.session.execute(
        select(Customer).where(Customer.email == customer_data['email'])
    ).scalars().first()
    if existing_email:
        return jsonify({"error": "Customer with this email already exists"}), 400

    # Check for existing phone
    existing_phone = db.session.execute(
        select(Customer).where(Customer.phone == customer_data['phone'])
    ).scalars().first()
    if existing_phone:
        return jsonify({"error": "Customer with this phone number already exists"}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201

# Get all customers
@customers_bp.route('', methods=['GET'])
def get_customers():

    customers = db.session.execute(select(Customer)).scalars().all()
    return customers_schema.jsonify(customers), 200

# Get customer by ID
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return customer_schema.jsonify(customer), 200

# Update customer
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# Delete customer
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer id: {customer_id} successfully deleted."}), 200
