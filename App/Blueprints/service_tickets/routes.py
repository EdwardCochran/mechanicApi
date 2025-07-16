from flask import Blueprint, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from App.models import db, ServiceTicket, Mechanic
from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema
from App.extensions import limiter, cache
from App.utils.util import encode_token, token_required

service_ticket_bp = Blueprint('service_ticket_bp', __name__)

# Create a service ticket
@service_ticket_bp.route('/', methods=['POST'])
def create_service_ticket():
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
@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
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
@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
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
@service_ticket_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_service_tickets():
    tickets = db.session.execute(select(ServiceTicket)).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200

# Get tickets for authenticated customer
@service_ticket_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    tickets = db.session.query(ServiceTicket).filter_by(customer_id=customer_id).all()
    return service_tickets_schema.jsonify(tickets), 200

# Delete service ticket
@service_ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
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
@service_ticket_bp.route('/<int:ticket_id>', methods=['PUT'])
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
