from flask import Blueprint, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from App.models import db, ServiceTicket, Mechanic
from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema
from App.extensions import limiter, cache
from App.utils.util import encode_token, token_required, decode_token  
from App.Blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, login_schema
from functools import wraps
from . import service_tickets_bp

# Create a service ticket
@service_tickets_bp.route('/', methods=['POST'])
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    existing_ticket = db.session.query(ServiceTicket).filter_by(
        vin=ticket_data['vin'],
        customer_id=ticket_data['customer_id'],
        service_description=ticket_data['service_description'],
        service_date=ticket_data['service_date']
    ).first()

    if existing_ticket:
        return jsonify({"message": "Service ticket already created"}), 200

    new_ticket = ServiceTicket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201

# Assign Mechanic to Ticket
@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@token_required
def assign_mechanic(customer_id, ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or Mechanic not found"}), 404

    if ticket.customer_id != customer_id:
        return jsonify({"error": "Unauthorized"}), 403

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned"}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

# Remove Mechanic from Ticket
@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@token_required
def remove_mechanic(customer_id, ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or Mechanic not found"}), 404

    if ticket.customer_id != customer_id:
        return jsonify({"error": "Unauthorized"}), 403

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic not assigned to this ticket"}), 200

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

# Get All Service Tickets (open/public — no auth)
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_service_tickets():
    tickets = db.session.execute(select(ServiceTicket)).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200

# Get tickets for authenticated customer
@service_tickets_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    tickets = db.session.query(ServiceTicket).filter_by(customer_id=customer_id).all()
    return service_tickets_schema.jsonify(tickets), 200

# Delete service ticket
@service_tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@token_required
@limiter.limit("4 per month")
def delete_service_ticket(customer_id, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    if ticket.customer_id != customer_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Service ticket id: {ticket_id} successfully deleted."}), 200

# Update service ticket
@service_tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@token_required
def update_service_ticket(customer_id, ticket_id):
    try:
        ticket_data = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    if ticket.customer_id != customer_id:
        return jsonify({"error": "Unauthorized"}), 403

    if 'vin' in ticket_data:
        ticket.vin = ticket_data['vin']
    if 'service_description' in ticket_data:
        ticket.service_description = ticket_data['service_description']
    if 'service_date' in ticket_data:
        ticket.service_date = ticket_data['service_date']

    if 'add_mechanic' in ticket_data:
        for mechanic_id in ticket_data['add_mechanic']:
            mechanic = db.session.get(Mechanic, mechanic_id)
            if not mechanic:
                return jsonify({"error": f"Mechanic with id {mechanic_id} not found"}), 404
            if mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)

    if 'remove_mechanic' in ticket_data:
        for mechanic_id in ticket_data['remove_mechanic']:
            mechanic = db.session.get(Mechanic, mechanic_id)
            if not mechanic:
                return jsonify({"error": f"Mechanic with id {mechanic_id} not found"}), 404
            if mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


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

@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket_mechanics(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data = request.get_json()
    add_ids = data.get('add_ids', [])
    remove_ids = data.get('remove_ids', [])

    # Add mechanics
    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic with ID {mechanic_id} not found"}), 404
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    # Remove mechanics
    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic with ID {mechanic_id} not found"}), 404
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200
