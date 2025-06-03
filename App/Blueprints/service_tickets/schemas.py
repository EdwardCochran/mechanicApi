from App.extensions import ma
from App.models import ServiceTicket

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
   class Meta:
        model = ServiceTicket
        include_fk = True

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

