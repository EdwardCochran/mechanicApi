from App import create_app # "App" is the folder that contains your __init__.py file
from App.models import db

app = create_app('DevelopmentConfig')

with app.app_context():
    db.create_all()
    
with app.app_context():
    if __name__ == '__main__':
        print("Registered routes:") #added lines 6-8 to print registered routes
        for rule in app.url_map.iter_rules():
            print(f"{rule.rule} -> {rule.endpoint}")

if __name__ == '__main__':
    app.run(debug=True)

# Marshmallow Schemas


#class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
#   class Meta:
#        model = ServiceTicket
#        include_fk = True

#service_ticket_schema = ServiceTicketSchema()
#service_tickets_schema = ServiceTicketSchema(many=True)

#class MechanicSchema(ma.SQLAlchemyAutoSchema):
#    class Meta:
#       model = Mechanic
#        include_fk = True

#mechanic_schema = MechanicSchema()
#mechanics_schema = MechanicSchema(many=True)

#    return service_ticket_schema.jsonify(new_service_ticket), 201



