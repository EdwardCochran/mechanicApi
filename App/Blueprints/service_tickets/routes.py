from flask import Blueprint, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from App.models import db, ServiceTicket, Mechanic
from .schemas import service_ticket_schema, service_tickets_schema

service_ticket_bp = Blueprint('service_ticket_bp', __name__)

#Create a service ticket
@service_ticket_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check for duplicate ticket
    existing_ticket = db.session.query(ServiceTicket).filter_by(
        vin=ticket_data['vin'],
        customer_id=ticket_data['customer_id'],
        service_description=ticket_data['service_description'],
        service_date=ticket_data['service_date']
    ).first()

    if existing_ticket:
        return jsonify({"message": "Service ticket already created"}), 200

    # Create new ticket
    new_ticket = ServiceTicket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201