from App.extensions import ma
from App.models import ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
   class Meta:
        model = ServiceTicket
        include_fk = True
        
from marshmallow import Schema, fields

class EditServiceTicketSchema(Schema):
    vin = fields.String()
    customer_id = fields.Integer()
    service_description = fields.String()
    service_date = fields.Date()
    add_mechanic = fields.List(fields.Integer(), required=False)
    remove_mechanic = fields.List(fields.Integer(), required=False)


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()