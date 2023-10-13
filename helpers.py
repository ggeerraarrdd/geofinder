from flask import redirect, render_template, session
from functools import wraps
from geographiclib.geodesic import Geodesic


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


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


def latitude_offset(lat, long):
    """Get latlng for first info window on game page."""

    geod = Geodesic.WGS84

    lat1 = lat
    lon1 = long
    theta = 0 #direction from North, clockwise 
    azi1 = theta - 0 #(90 degrees to the left)
    shift = 201 #meters

    g = geod.Direct(lat1, lon1, azi1, shift)

    lat2 = g['lat2']
    lon2 = g['lon2']

    return(lat2)
