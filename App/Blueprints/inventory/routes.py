from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

from App.extensions import db
from App.models import Inventory
from .schemas import inventory_schema, inventories_schema

inventory_bp = Blueprint("inventory_bp", __name__)


@inventory_bp.route("", methods=["POST"])
def create_part():
    try:
        part_data = inventory_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    part = Inventory(**part_data)
    db.session.add(part)
    db.session.commit()
    return inventory_schema.jsonify(part), 201


@inventory_bp.route("", methods=["GET"])
def list_parts():
    parts = db.session.execute(select(Inventory)).scalars().all()
    return inventories_schema.jsonify(parts), 200


@inventory_bp.route("/<int:part_id>", methods=["GET"])
def get_part(part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    return inventory_schema.jsonify(part), 200


@inventory_bp.route("/<int:part_id>", methods=["PUT"])
def update_part(part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    try:
        update_data = inventory_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, value in update_data.items():
        setattr(part, key, value)

    db.session.commit()
    return inventory_schema.jsonify(part), 200


@inventory_bp.route("/<int:part_id>", methods=["DELETE"])
def delete_part(part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part id {part_id} deleted"}), 200
