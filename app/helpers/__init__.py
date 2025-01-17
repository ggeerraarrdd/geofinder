# Python Standard Library
from functools import wraps

# Third-Party Libraries
from flask import redirect, session

# Local
from .helpers_geospatial import *





def apology(message, code=400):

    session.pop("error_message", None)

    """
    Escape special characters.

    https://github.com/jacebrowning/memegen#special-characters
    """
    for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
        message = message.replace(old, new)
    
    session["error_message"] = f'http://api.memegen.link/grumpycat/{code}/{message}.jpg&width=300"'
    
    return redirect("/error")


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        
        return f(*args, **kwargs)
    return decorated_function
