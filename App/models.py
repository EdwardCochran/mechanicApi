from App.extensions import db

service_mechanic = db.Table(
    "service_mechanic",
    db.Column("ticket_id", db.Integer, db.ForeignKey("service_ticket.id")),
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanic.id"))
)

service_inventory = db.Table(
    "service_inventory",
    db.Column("ticket_id", db.Integer, db.ForeignKey("service_ticket.id")),
    db.Column("inventory_id", db.Integer, db.ForeignKey("inventory.id"))
)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tickets = db.relationship("ServiceTicket", backref="customer", lazy=True)

    # implement set_password / check_password helpers if not present

class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Float, nullable=True)
    tickets = db.relationship("ServiceTicket", secondary=service_mechanic, back_populates="mechanics")

class ServiceTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(120), nullable=False)
    service_description = db.Column(db.String(255), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    mechanics = db.relationship("Mechanic", secondary=service_mechanic, back_populates="tickets")
    parts = db.relationship("Inventory", secondary=service_inventory, back_populates="tickets")

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    tickets = db.relationship("ServiceTicket", secondary=service_inventory, back_populates="parts")
