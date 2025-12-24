from App.extensions import ma
from App.models import Inventory


class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = False


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
