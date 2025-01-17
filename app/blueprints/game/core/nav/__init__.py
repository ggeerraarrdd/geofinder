from flask import Blueprint

nav_bp = Blueprint('nav_bp', __name__)

from . import routes
