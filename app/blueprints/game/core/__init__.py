from flask import Blueprint

# # Import submodules
# from .authy import routes
# from .profile import profile
# from .nav import nav
# from .main import main





# Initialize the blueprint
authy_bp = Blueprint('authy_bp',
                    __name__,
                    static_folder='static', 
                    static_url_path='/game/core/static',
                    template_folder='templates')

main_bp = Blueprint('main_bp',
                    __name__,
                    static_folder='static', 
                    static_url_path='/game/core/static',
                    template_folder='templates')

nav_bp = Blueprint('nav_bp',
                    __name__,
                    static_folder='static', 
                    static_url_path='/game/core/static',
                    template_folder='templates')

profile_bp = Blueprint('profile_bp',
                    __name__,
                    static_folder='static', 
                    static_url_path='/game/core/static',
                    template_folder='templates')

# Register routes
from .authy import routes
from .profile import routes
from .nav import routes
from .main import routes