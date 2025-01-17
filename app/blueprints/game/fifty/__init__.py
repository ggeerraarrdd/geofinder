from flask import Blueprint





# Initialize the blueprint
fifty_bp = Blueprint('fifty_bp',
                    __name__,
                    static_folder='static', 
                    static_url_path='/game/fifty/static',
                    template_folder='templates')

# Import routes
from . import routes
