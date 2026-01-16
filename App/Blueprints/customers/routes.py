from flask import  request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from App.models import Customer, db
from .schemas import customer_schema, customers_schema, login_schema
from . import customers_bp
from App.extensions import limiter, cache
from App.utils.util import encode_token, token_required


@customers_bp.route('/login', methods=['POST'])
def login():
    try:
        # Validate request with schema
        credentials = login_schema.load(request.get_json())
        email = credentials.get('email')
        password = credentials.get('password')
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    # Look up user in DB
    customer = db.session.execute(
        select(Customer).where(Customer.email == email)
    ).scalar_one_or_none()

    # Authenticate user
    if customer and customer.password == password:
        token = encode_token(customer.id)
        return jsonify({
            "status": "success",
            "message": "Logged in successfully",
            "auth_token": token
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
#Create Customer
@customers_bp.route('', methods=['POST'])
@limiter.limit("25 per day")  # Limit signups to reduce abuse/spam account creation
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
@cache.cached(timeout=60)  # Cache list to speed up repeated access
def get_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    per_page = min(per_page, 50)  # cap page size to avoid overload

    pagination = db.paginate(select(Customer), page=page, per_page=per_page, error_out=False)
    return (
        jsonify(
            {
                "items": customers_schema.dump(pagination.items),
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            }
        ),
        200,
    )

# Get customer by ID
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return customer_schema.jsonify(customer), 200

# Update customer
@customers_bp.route('/', methods=['PUT'])
@token_required
@limiter.limit("4 per month")  # Slow down profile edits to reduce accidental/abusive activity
def update_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
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
@customers_bp.route('/', methods=['DELETE'])
@token_required
@limiter.limit("3 per day")  # Protect against rapid account deletions or malicious abuse
def delete_customer(customer_id): #Retreiving customer.id by token
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer id: {customer_id} successfully deleted."}), 200
