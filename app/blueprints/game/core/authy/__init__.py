from flask import Blueprint

authy_bp = Blueprint('authy_bp', __name__)

from . import routes