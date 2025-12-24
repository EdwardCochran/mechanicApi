from App.extensions import ma
from App.models import Customer
from marshmallow import Schema, fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


class CustomerLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerLoginSchema()
