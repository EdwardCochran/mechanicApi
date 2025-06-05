from App.extensions import ma
from App.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema= MechanicSchema(only=('email', 'password'))  # For login, only email and password are needed