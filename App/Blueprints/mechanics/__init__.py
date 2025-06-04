from flask import Blueprint
from .routes import mechanic_bp

mechanics_bp = Blueprint('mechanics_bp', __name__)

from . import routes