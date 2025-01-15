# Python Standard Library
import os

# Third-Party Libraries
from flask import Flask
from flask_session import Session

# Local Modules
from blueprints.game.main import main
from blueprints.game.authy import authy
from blueprints.game.nav import nav
from blueprints.game.profile import profile
from blueprints.game.fifty import fifty





# Configure application
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# Set constant variables
MAP_API_KEY = os.environ.get("MAP_API_KEY")
DATABASE_PG = os.environ.get("DATABASE_PG")

# View HTML changes without rerunning server
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure session
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(authy)
app.register_blueprint(nav)
app.register_blueprint(profile)
app.register_blueprint(fifty)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
