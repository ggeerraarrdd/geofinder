import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_socketio import SocketIO
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import shapely.wkb
import json

import queries
from helpers import apology, login_required, latitude_offset, longitude_offset
from geoshapefile import shapefile, get_distance
from shapely.geometry import Point


# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

socketio = SocketIO(app)

# View HTML changes without rerunning server
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set environmental variables
map_api_key = os.environ.get("MAP_API_KEY")
host = os.environ.get("GEOFINDER_DB_HOST")
port = os.environ.get("GEOFINDER_DB_PORT")
database = os.environ.get("GEOFINDER_DB_NAME")
user = os.environ.get("GEOFINDER_DB_USER")
password = os.environ.get("GEOFINDER_DB_PASSWORD")

# Set database
db_pg = f'postgresql://{user}:{password}@{host}:{port}/{database}'

# Set registration status
try:
    new_registrations = False if os.environ.get("NEW_REGISTRATIONS").upper() == "FALSE" else True
except:
    new_registrations = False


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# @socketio.on('disconnect')
# def disconnect():

#     current_game_id = session["current_game_id"]
#     current_game_start = session['current_game_start']

#     result = queries.get_disconnected(db_pg, 
#                                       current_game_id, 
#                                       current_game_start)

#     return 1


@app.route('/disconnect', methods=['POST'])
def disconnect():

    data = json.loads(request.data)
    message = data['message']

    if message == "8dc4ed2b-4e99-45f7-a6a2-319ccb31d17d":
        current_game_id = session["current_game_id"]
        current_game_start = session['current_game_start']

        result = queries.get_disconnected(db_pg, 
                                          current_game_id, 
                                          current_game_start)

        return '', 200

    else:

        return '', 200


####################################################################
# 
# INDEX
#
####################################################################
@app.route("/")
@login_required
def index():
    """Show homepage"""

    try:
        page = session["current_page"]
        goto = session["current_goto"]
    except KeyError:
        page = None
        goto = "index" 
    
    # Calculate user summary percent
    session["user_summary_percent"] = queries.get_summary_percent(db_pg, 
                                                                  session["user_id"])

    # Ensure session page is set to index before index.html is rendered
    session.pop("page", None)
    session["page"] = "index"

    return render_template("index.html", 
                           page="index", 
                           userid=session["user_id"], 
                           username=session["username"], 
                           total1=session["user_summary_percent"],
                           map_api_key=map_api_key,
                           new_registrations=new_registrations)


####################################################################
# 
# GAME
#
####################################################################
@app.route("/game", methods=["GET", "POST"])
@login_required
def game():
    """Start a game"""

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        try_again = session["try_again"] = request.form.get("try-again")

        if "current_game_id" not in session:
            session["current_game_id"] = 0

    else:

        page = session["current_page"]
        goto = session["current_goto"]
        try_again = session["try_again"]

        if "current_game_id" not in session:
            session["current_game_id"] = 0

    # Clean-up session
    # Leave only user_id and username
    # And current_game_loc_id - will be cleared if user starts new game
    session.pop("current_game_id", None)
    session.pop("current_game_loc_view_lat", None)
    session.pop("current_game_loc_view_lng", None)
    session.pop("current_game_loc_key_shp", None)
    session.pop("current_game_loc_key_lat", None)
    session.pop("current_game_loc_key_lng", None)
    session.pop("current_game_user_submit_lat", None)
    session.pop("current_game_user_submit_lng", None)
    session.pop("current_game_start", None)
    session.pop("current_game_map_center", None)
    session.pop("current_game_map_zoom", None)

    # Get playable location
    if (session["try_again"] == "1") or (session["try_again"] == 1):
        # Get specific location to try again
        location = queries.get_playable_location_again(db_pg, 
                                                       session["current_game_loc_id"])
    else:
        # Get random location as new game
        location = queries.get_playable_location(db_pg, 
                                                 session["user_id"])

    # Checks if query returns a playable location
    if location == None:
        return redirect("/history")
    else:
        # Update session with location info to be played
        session["current_game_loc_id"] = location["id"]
        session["current_game_loc_key_shp"] = location["loc_key_shp"]
        session["current_game_loc_key_lat"] = location["loc_key_lat"]
        session["current_game_loc_key_lng"] = location["loc_key_lng"]

        # Create new entry in games table
        current_game_id, current_game_start = queries.start_game(db_pg, 
                                                                 session["user_id"], 
                                                                 session["current_game_loc_id"])
        
        # Get hour, minute and seconds from current_game_start
        clock = {
            "hour": current_game_start.hour,
            "minute": current_game_start.minute,
            "second": current_game_start.second
        }

        # Update session with game info to be played
        session["current_game_loc_id"] = location["id"]
        session["current_game_loc_view_lat"] = location["loc_view_lat"]
        session["current_game_loc_view_lng"] = location["loc_view_lng"]
        session["current_game_loc_key_shp"] = location["loc_key_shp"]
        session["current_game_loc_key_lat"] = location["loc_key_lat"]
        session["current_game_loc_key_lng"] = location["loc_key_lng"]
        session["current_game_id"] = current_game_id
        session["current_game_start"] = current_game_start

        # Get offset latitude to position infowindow on map
        loc_lat_game_offset = latitude_offset(float(location["loc_view_lat"]), 
                                              float(location["loc_view_lng"]))

        # Ensure session page is set to "game" before game.html is rendered
        session["page"] = "game"

    return render_template("game.html", 
                           page="game", 
                           username=session["username"], 
                           total1=session["user_summary_percent"],
                           location=location, 
                           loc_lat_game_offset=loc_lat_game_offset, 
                           clock=clock, 
                           map_api_key=map_api_key)


####################################################################
#
# RESULT
#
####################################################################
@app.route("/result", methods=["GET", "POST"])
@login_required
def result():
    """Submit game"""

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")

        if (page == "game") and (goto == "result"):

            # Set current timestamp
            current_game_end = datetime.now()

            # Get user-submitted answer
            current_game_user_submit_lat = float(request.form.get("answer-lat"))
            current_game_user_submit_lng = float(request.form.get("answer-long"))
            
            # Update session
            session["current_game_user_submit_lat"] = current_game_user_submit_lat
            session["current_game_user_submit_lng"] = current_game_user_submit_lng 
            session["current_game_map_center"] = request.form.get("answer-map-center")
            session["current_game_map_zoom"] = request.form.get("answer-map-zoom")

            # Get location answer 
            current_game_loc_key_lat = session["current_game_loc_key_lat"]
            current_game_loc_key_lng = session["current_game_loc_key_lng"]

            # Get location key shapefile
            current_game_loc_key_shapefile = session["current_game_loc_key_shp"]

            # Convert the PostGIS geometry into a Shapely geometry object
            polygon = shapely.wkb.loads(current_game_loc_key_shapefile, hex=True)

            # Create a point object from user submitted (lat, lng)
            point = Point([current_game_user_submit_lng, current_game_user_submit_lat])

            # Check if point is inside polygon
            is_inside = polygon.contains(point)

            # Validate answer as 1 = "correct" or 0 = "incorrect"
            if is_inside:
                game_answer_distance = 0
                game_answer_validation = 1
                current_game_answer_user_validation = "correct!"
            else:
                game_answer_distance = get_distance(point, polygon)
                game_answer_validation = 0
                current_game_answer_user_validation = "incorrect"

            # Calcuate game duration in minutes
            durations = queries.game_answer_duration(session["current_game_start"], 
                                                     current_game_end)

            # Calcuate game duration for all previous attempts in minutes
            duration_total = queries.get_loc_duration_total(db_pg, 
                                                            session["current_game_id"], 
                                                            session["user_id"], 
                                                            session["current_game_loc_id"], 
                                                            durations[0])

            # Calculate game score
            scores = queries.game_answer_score(db_pg, 
                                               session["user_id"], 
                                               session["current_game_loc_id"], 
                                               game_answer_validation, 
                                               duration_total)
            base_score = scores[0]
            bonus_score = scores[1]
            game_score = scores[2]
            attempts = scores[3]

            # Set update_current_game arguments
            updates = {
                "id": session["current_game_id"], 
                "game_end": current_game_end,
                "game_lat": current_game_user_submit_lat,
                "game_lng": current_game_user_submit_lng,
                "game_user_quit": 0,
                "game_answer_off": game_answer_distance,
                "game_answer_validation": game_answer_validation,
                "game_duration": durations[0],
                "game_score": game_score
            }

            # Update games table
            queries.update_current_game(db_pg, updates)

            # Update session with new total score
            session["user_summary_percent"] = queries.get_summary_percent(db_pg, session["user_id"])

            # Create dictionary for html page
            results = {
                "current_game_loc_view_lat": session["current_game_loc_view_lat"],
                "current_game_loc_view_lng": session["current_game_loc_view_lng"],
                "current_game_user_submit_lat": current_game_user_submit_lat,
                "current_game_user_submit_lng": current_game_user_submit_lng,
                "answer_validation": game_answer_validation,
                "current_game_answer_user_validation": current_game_answer_user_validation,
                "current_game_loc_id": session["current_game_loc_id"],
                "current_game_loc_attempt": attempts,
                "current_game_duration": durations[0],
                "current_location_duration": duration_total,
                "current_game_score_base": base_score,
                "current_game_score_bonus": bonus_score,
                "current_game_score_total": game_score
            }

            # Ensure session page is set to "result" before submit.html is rendered
            session["page"] = "result"

            return render_template("submit.html", 
                                   data=results, 
                                   page="result", 
                                   username=session["username"], 
                                   total1=session["user_summary_percent"], 
                                   map_api_key=map_api_key)
        
        else:

            # Ensure current_game_loc_id is cleared
            session.pop("current_game_loc_id", None)

            # Ensure session page is cleared before redirecting to "/"
            session.pop("page", None)

            return redirect("/")
            
    else:

        page = session["current_page"]
        goto = session["current_goto"]

        if (page == "game") and (goto == "zero"):

            # Get info on current game
            current_game_record = queries.get_game_info(db_pg, session["current_game_id"])

            # Get info on location of current game
            current_game_loc_record = queries.get_locs_info(db_pg, session["current_game_loc_id"])

            # Calcuate game duration for all previous attempts in minutes
            duration_total = queries.get_loc_duration_total(db_pg, 
                                                            session["current_game_id"], 
                                                            session["user_id"], 
                                                            session["current_game_loc_id"], 
                                                            current_game_record["game_duration"])

            # Calculate total attempts
            scores = queries.game_answer_score(db_pg, 
                                               session["user_id"], 
                                               session["current_game_loc_id"], 
                                               current_game_record["game_answer_validation"], 
                                               duration_total)
            attempts = scores[3]

            # Create dictionary for html page
            results = {
                "current_game_loc_view_lat": session["current_game_loc_view_lat"],
                "current_game_loc_view_lng": session["current_game_loc_view_lng"],
                "current_game_user_submit_lat": current_game_loc_record["loc_key_lat"],
                "current_game_user_submit_lng": current_game_loc_record["loc_key_lng"],
                "answer_validation": current_game_record["game_answer_validation"],
                "current_game_answer_user_validation": "quit",
                "current_game_loc_id": current_game_loc_record["id"],
                "current_game_loc_attempt": attempts,
                "current_game_duration": current_game_record["game_duration"],
                "current_location_duration": duration_total,
                "current_game_score_base": 0,
                "current_game_score_bonus": 0,
                "current_game_score_total": 0
            }

            # Ensure current_game_loc_id is cleared
            session.pop("current_game_loc_id", None)

            return render_template("submit.html", 
                                   data=results, 
                                   page="result", 
                                   username=session["username"], 
                                   total1=session["user_summary_percent"],
                                   map_api_key=map_api_key)

        else:

            # Ensure current_game_loc_id is cleared
            session.pop("current_game_loc_id", None)

            # Ensure session page is cleared before redirecting to "/"
            session.pop("page", None)

            return redirect("/")


####################################################################
# 
# ABOUT
#
####################################################################
@app.route("/about", methods=["GET", "POST"])
def about():
    """Get about page."""

    # Get values from session
    try:
        userid = session["user_id"]
    except KeyError:
        userid = 0
    
    try:
        username = session["username"]
    except KeyError:
        username = None
    
    try:
        total1 = session["user_summary_percent"]
    except KeyError:
        total1 = 0

    # Ensure session page is set to "about" before about.html is rendered
    session["page"] = "about"
    
    return render_template("about.html", 
                           page="about", 
                           userid=userid, 
                           username=username, 
                           total1=total1,
                           map_api_key=map_api_key,
                           new_registrations=new_registrations)


####################################################################
# 
# HOW TO PLAY
#
####################################################################
@app.route("/howto", methods=["GET", "POST"])
def howto():
    """Get how to page"""

    # Get values from session
    try:
        userid = session["user_id"]
    except KeyError:
        userid = 0
    
    try:
        username = session["username"]
    except KeyError:
        username = None
    
    try:
        total1 = session["user_summary_percent"]
    except KeyError:
        total1 = 0

    # Ensure session page is set to "howto" before howto.html is rendered
    session["page"] = "howto"
    
    return render_template("howto.html", 
                           page="howto", 
                           userid=userid, 
                           username=username, 
                           total1=total1, 
                           map_api_key=map_api_key,
                           new_registrations=new_registrations)


####################################################################
# 
# PROFILE
#
####################################################################
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Get how to page"""

    # Get values from session
    try:
        userid = session["user_id"]
    except KeyError:
        userid = 0
    
    try:
        username = session["username"]
    except KeyError:
        username = None
    
    try:
        total1 = session["user_summary_percent"]
    except KeyError:
        total1 = 0

    profile = queries.get_profile_user(db_pg,
                                       userid)
    
    results = queries.get_profile_summary(db_pg, 
                                          userid)

    try:
        profile_message_username = session["profile_message_username"]
    except KeyError:
        profile_message_username = "None"

    try:
        profile_message_country = session["profile_message_country"]
    except KeyError:
        profile_message_country = "None"
    
    try:
        profile_message_password = session["profile_message_password"]
    except KeyError:
        profile_message_password = "None"

    # Ensure session messages cleared
    session.pop("profile_message_username", None)
    session.pop("profile_message_country", None)
    session.pop("profile_message_password", None)
    
    # Ensure session page is set to "howto" before howto.html is rendered
    session["page"] = "profile"
    
    return render_template("profile.html", 
                           page="profile", 
                           userid=userid, 
                           username=username, 
                           total1=total1, 
                           map_api_key=map_api_key,
                           profile=profile,
                           data=results,
                           profile_message_username=profile_message_username,
                           profile_message_country=profile_message_country,
                           profile_message_password=profile_message_password)


####################################################################
# 
# PROFILE - GEO50X
#
####################################################################
@app.route("/profile/fifty", methods=["GET", "POST"])
@login_required
def profile_fifty():
    """Show user history of games """

    if request.method == "POST":

        return redirect("/")
    
    else:

        summaries = queries.get_profile_summary(db_pg, session["user_id"])

        locs_playable_count, history = queries.get_history(db_pg, session["user_id"])

        # Ensure session page is set to "history" before history.html is rendered
        session["page"] = "profile_fifty"

        return render_template("profile_fifty.html", 
                               page="profile_fifty", 
                               summary=summaries,
                               locs_playable_count=locs_playable_count, 
                               history=history, 
                               userid=session["user_id"], 
                               username=session["username"], 
                               total1=summaries["user_score_percentage"], 
                               map_api_key=map_api_key)


####################################################################
# 
# PROFILE - EDIT
#
####################################################################
@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    """Show user history of games """

    if request.method == "POST":

        username = request.form.get("username")
        country = request.form.get("country")
        pass_old = request.form.get("pass_old")
        pass_new = request.form.get("pass_new")
        pass_again = request.form.get("pass_again")

        if username:
            results = queries.get_profile_updated_username(db_pg, 
                                                           username, 
                                                           session["user_id"])
            
            if results == 1:
                session["profile_message_username"] = "Username changed"
                session["username"] = username
            else:
                session["profile_message_username"] = "Username not changed"

        if country:
            results = queries.get_profile_updated_country(db_pg, 
                                                          country, 
                                                          session["user_id"])
            
            if results == 1:
                session["profile_message_country"] = "Country changed"
            else:
                session["profile_message_country"] = "Country not changed"
        
        if pass_old:
            user = queries.get_user_info(db_pg, session["username"])

            if len(user) < 1 or not check_password_hash(user["hash"], pass_old):
                session["profile_message_password"] = "Wrong password"

            if pass_new == pass_again:
                new_password = generate_password_hash(pass_again)
                try:
                    queries.get_profile_updated_password(db_pg, new_password, session["user_id"])
                    session["profile_message_password"] = "New password saved"
                except (ValueError, RuntimeError):
                    session["profile_message_password"] = "New password not saved"
            else:
                session["profile_message_password"] = "New password did not match"

        return redirect("/profile")
    
    else:

        return redirect("/")
    

####################################################################
# 
# ADMIN - DASHBOARD - MAIN
#
####################################################################
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    """Show user history of games """

    if request.method == "POST":

        if session["status"] == "admin":
 
            loc_id = int(request.form.get("loc-edit"))

            if loc_id > 0:

                location = queries.get_locs_single(db_pg, loc_id)

                if location["loc_key_shp"]:

                    # Convert the PostGIS geometry into a Shapely geometry object
                    geometry = shapely.wkb.loads(location["loc_key_shp"], hex=True)

                    # Extract the polygon coordinates
                    polygon_coordinates = list(geometry.exterior.coords)
                    
                    # Convert the polygon coordinates into a format suitable for the Google Maps API
                    polygon = []
                    for coordinate in polygon_coordinates:
                        polygon.append({"lat": coordinate[1], "lng": coordinate[0]})
                    
                    # Convert the Google Maps polygon to JSON
                    google_maps_polygon = json.dumps(polygon)    

                else:
                    google_maps_polygon = queries.get_locs_corners(float(location["loc_key_lat"]), 
                                                                float(location["loc_key_lng"]))
                    
                    google_maps_polygon = json.dumps(google_maps_polygon)   

                # Ensure session page is set to "locs-edit" before locs_edit.html is rendered
                session["page"] = "locs-edit"
            
                return render_template("locs_edit.html", 
                                        data=location, 
                                        polygon=google_maps_polygon,
                                        page="locs-edit", 
                                        userid=session["user_id"], 
                                        username=session["username"], 
                                        total1=session["user_summary_percent"], 
                                        map_api_key=map_api_key)
            
            elif loc_id == 0:

                result = queries.get_locs_refreshed(db_pg)

                return redirect("/locs")

            else:

                return redirect("/")
        
        else:

            return redirect("/")
    
    else:

        if session["status"] == "admin":

            keys = queries.get_locs(db_pg)

            # Ensure session page is set to "history" before history.html is rendered
            session["page"] = "history"

            return render_template("admin.html", 
                                keys=keys,
                                page="keys", 
                                userid=session["user_id"], 
                                username=session["username"], 
                                total1=session["user_summary_percent"], 
                                map_api_key=map_api_key)
        
        else:

            return redirect("/")
        

####################################################################
# 
# ADMIN - DASHBOARD - GEO50x
#
####################################################################
@app.route("/admin/fifty", methods=["GET", "POST"])
@login_required
def admin_fifty():
    """Show user history of games """

    if request.method == "POST":

        if session["status"] == "admin":
 
            loc_id = int(request.form.get("loc-edit"))

            if loc_id > 0:

                location = queries.get_locs_single(db_pg, loc_id)

                if location["loc_key_shp"]:

                    # Convert the PostGIS geometry into a Shapely geometry object
                    geometry = shapely.wkb.loads(location["loc_key_shp"], hex=True)

                    # Extract the polygon coordinates
                    polygon_coordinates = list(geometry.exterior.coords)
                    
                    # Convert the polygon coordinates into a format suitable for the Google Maps API
                    polygon = []
                    for coordinate in polygon_coordinates:
                        polygon.append({"lat": coordinate[1], "lng": coordinate[0]})
                    
                    # Convert the Google Maps polygon to JSON
                    google_maps_polygon = json.dumps(polygon)    

                else:
                    google_maps_polygon = queries.get_locs_corners(float(location["loc_key_lat"]), 
                                                                float(location["loc_key_lng"]))
                    
                    google_maps_polygon = json.dumps(google_maps_polygon)   

                # Ensure session page is set to "locs-edit" before locs_edit.html is rendered
                session["page"] = "admin_fifty_edit"
            
                return render_template("admin_fifty_edit.html", 
                                        data=location, 
                                        polygon=google_maps_polygon,
                                        page="admin_fifty_edit", 
                                        userid=session["user_id"], 
                                        username=session["username"], 
                                        total1=session["user_summary_percent"], 
                                        map_api_key=map_api_key)
            
            elif loc_id == 0:

                result = queries.get_locs_refreshed(db_pg)

                return redirect("/admin/fifty")

            else:

                return redirect("/")
        
        else:

            return redirect("/")
    
    else:

        if session["status"] == "admin":

            locs_fifty = queries.get_locs(db_pg)

            locs_fifty_status = queries.get_locs_fifty_status(db_pg)

            # Ensure session page is set to "admin_fifty" before admin_fifty.html.html is rendered
            session["page"] = "admin_fifty"

            return render_template("admin_fifty.html", 
                                    locs=locs_fifty,
                                    page="admin_fifty", 
                                    locs_fifty_status=locs_fifty_status,
                                    userid=session["user_id"], 
                                    username=session["username"], 
                                    total1=session["user_summary_percent"], 
                                    map_api_key=map_api_key)
        
        else:

            return redirect("/")
        

####################################################################
# 
# ADMIN - DASHBOARD - GEO50x - EDIT
#
####################################################################
@app.route("/admin/fifty/edit", methods=["GET", "POST"])
@login_required
def admin_fifty_edit():
    """Show user history of games """

    if request.method == "POST":

        if session["status"] == "admin":
 
            loc_id = request.form.get("loc-id")
            property_coordinates = request.form.get("propertyCoordinates")

            if loc_id: 

                if property_coordinates:

                    # Convert string to list
                    property_coordinates = eval("[" + property_coordinates + "]")

                    # Convert to list of dicts
                    property_coordinates = [{"lat": lat, "lng": lng} for lat, lng in property_coordinates]

                    result = shapefile(db_pg, property_coordinates, int(loc_id))

                    return redirect("/admin/fifty")

                else:

                    return redirect("/admin/fifty")
            
            else: 
    
                return redirect("/admin/fifty")
        
        else:

            return redirect("/")
    
    else:

        if session["status"] == "admin":

            return redirect("/")
        
        else:

            return redirect("/")
        

####################################################################
# 
# ADMIN - DASHBOARD - USERS
#
####################################################################
@app.route("/admin/users", methods=["GET", "POST"])
@login_required
def admin_users():
    """Show user history of games """

    if request.method == "POST":

        profile_message_username = ""
        profile_message_country = ""
        profile_message_password = ""
        
        if session["status"] == "admin":
 
            userid = request.form.get("admin-user-id")

            profile = queries.get_profile_user(db_pg,
                                               userid)

            results = queries.get_profile_summary(db_pg, 
                                                  userid)

            try:
                profile_message_username = session["profile_message_username"]
            except KeyError:
                profile_message_username = "None"

            try:
                profile_message_country = session["profile_message_country"]
            except KeyError:
                profile_message_country = "None"

            try:
                profile_message_password = session["profile_message_password"]
            except KeyError:
                profile_message_password = "None"

            # Ensure session messages cleared
            session.pop("profile_message_username", None)
            session.pop("profile_message_country", None)
            session.pop("profile_message_password", None)

            # Ensure session page is set to "howto" before howto.html is rendered
            session["page"] = "profile"

            return render_template("admin_users_edit.html", 
                                    page="profile", 
                                    userid=session["user_id"], 
                                    username=session["username"], 
                                    total1=session["user_summary_percent"], 
                                    map_api_key=map_api_key,
                                    profile=profile,
                                    data=results,
                                    profile_message_username=profile_message_username,
                                    profile_message_country=profile_message_country,
                                    profile_message_password=profile_message_password)
        
        else:

            return redirect("/")
    
    else:

        if session["status"] == "admin":

            header = queries.get_header_admin_users(db_pg)
            users = queries.get_table_admin_users(db_pg)

            # Ensure session page is set to "admin_fifty" before admin_fifty.html.html is rendered
            session["page"] = "admin_users"

            return render_template("admin_users.html", 
                                    page="admin_fifty", 
                                    userid=session["user_id"], 
                                    username=session["username"], 
                                    total1=session["user_summary_percent"], 
                                    map_api_key=map_api_key,
                                    header=header,
                                    users=users)
        
        else:

            return redirect("/")


####################################################################
# 
# ADMIN - DASHBOARD - USERS - EDIT
#
####################################################################
@app.route("/admin/users/edit", methods=["GET", "POST"])
@login_required
def admin_users_edit():

    if request.method == "POST":

        if session["status"] == "admin":

            profile_message_username = ""
            profile_message_country = ""
            profile_message_password = ""

            admin_edit_user_id = request.form.get("admin-user-id")
            username = request.form.get("username")
            country = request.form.get("country")
            # pass_old = request.form.get("pass_old")
            pass_new = request.form.get("pass_new")
            pass_again = request.form.get("pass_again")

            if username:
                results = queries.get_profile_updated_username(db_pg, 
                                                               username, 
                                                               admin_edit_user_id)
                
                if results == 1:
                    session["profile_message_username"] = "Username changed"
                else:
                    session["profile_message_username"] = "Username not changed"

            if country:
                results = queries.get_profile_updated_country(db_pg, 
                                                              country, 
                                                              admin_edit_user_id)
                
                if results == 1:
                    session["profile_message_country"] = "Country changed"
                else:
                    session["profile_message_country"] = "Country not changed"

            if pass_new:
                if pass_new == pass_again:
                    new_password = generate_password_hash(pass_again)
                    try:
                        queries.get_profile_updated_password(db_pg, new_password, admin_edit_user_id)
                        session["profile_message_password"] = "New password saved"
                    except (ValueError, RuntimeError):
                        session["profile_message_password"] = "New password not saved"
                else:
                    session["profile_message_password"] = "New password did not match"

            profile = queries.get_profile_user(db_pg,
                                               admin_edit_user_id)

            results = queries.get_profile_summary(db_pg, 
                                                  admin_edit_user_id)

            try:
                profile_message_username = session["profile_message_username"]
            except KeyError:
                profile_message_username = "None"

            try:
                profile_message_country = session["profile_message_country"]
            except KeyError:
                profile_message_country = "None"

            try:
                profile_message_password = session["profile_message_password"]
            except KeyError:
                profile_message_password = "None"

            # Ensure session messages cleared
            session.pop("profile_message_username", None)
            session.pop("profile_message_country", None)
            session.pop("profile_message_password", None)

            # Ensure session page is set to "howto" before howto.html is rendered
            session["page"] = "profile"

            return render_template("admin_users_edit.html", 
                                    page="profile", 
                                    userid=session["user_id"], 
                                    username=session["username"], 
                                    total1=session["user_summary_percent"], 
                                    map_api_key=map_api_key,
                                    profile=profile,
                                    data=results,
                                    profile_message_username=profile_message_username,
                                    profile_message_country=profile_message_country,
                                    profile_message_password=profile_message_password)
        
        else:

            return redirect("/")
    
    else:

        return redirect("/")
        

####################################################################
# 
# ADMIN - DASHBOARD - USERS - ADD
#
####################################################################
@app.route("/admin/users/add", methods=["GET", "POST"])
@login_required
def admin_users_add():

    if request.method == "POST":

        if session["status"] == "admin":

            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)
            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 400)
            else:
                # Ensure password and confirmation match
                new_password = request.form.get("password")
                confirmation = request.form.get("confirmation")
                if new_password == confirmation:
                    new_username = request.form.get("username")
                    new_password = generate_password_hash(confirmation)
                    try:
                        queries.get_registered(db_pg, new_username, new_password)
                    except (ValueError, RuntimeError):
                        return apology("username is already taken", 400)
                    return redirect("/admin/users")
                else:
                    return apology("password did not match", 400)
        
        else:

            return redirect("/")
    
    else:
        
        if session["status"] == "admin":

            # Ensure session page is set to "register" before register.html is rendered
            session["page"] = "register"

            return render_template("admin_users_add.html", 
                                   page="register", 
                                   userid=session["user_id"], 
                                   username=session["username"], 
                                   total1=session["user_summary_percent"], 
                                   map_api_key=map_api_key,
                                   button="bttn-admin")
    
        else:

            return redirect("/")
        

####################################################################
# 
# HISTORY
#
####################################################################
@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show user history of games """

    if request.method == "POST":

        return redirect("/")
    
    else:

        locs_playable_count, history = queries.get_history(db_pg, session["user_id"])

        # Ensure session page is set to "history" before history.html is rendered
        session["page"] = "history"

        return render_template("history.html", 
                            page="history", 
                            locs_playable_count=locs_playable_count, 
                            history=history, userid=session["user_id"], 
                            username=session["username"], 
                            total1=session["user_summary_percent"], 
                            map_api_key=map_api_key)


####################################################################
# 
# REVIEW
#
####################################################################
@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    """Review game"""

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        review = request.form.get("review")

        loc_info, locations_right, locations_wrong, locations_none, locations_quit, time_clock = queries.get_history_review(db_pg, session["user_id"], review)

        # Get offset latitude to position infowindow on map
        loc_lat_game_offset = latitude_offset(float(loc_info["loc_view_lat"]), float(loc_info["loc_view_lng"]))

        locations_shift = []
        shift = 221
        for i in range(locations_none["count"]):
            lat, lng = longitude_offset(float(loc_info["loc_view_lat"]), float(loc_info["loc_view_lng"]), shift)
            
            latlng = {"game_lat": str(lat), "game_lng": str(lng)}
            locations_shift.append(latlng)
            
            i += 1
            shift += 20

        return render_template("review.html", 
                               location=loc_info, 
                               locations_right=locations_right, 
                               locations_wrong=locations_wrong, 
                               locations_none=locations_shift,
                               locations_quit=locations_quit, 
                               time_clock=time_clock["time_clock"], 
                               username=session["username"], 
                               total1=session["user_summary_percent"], 
                               loc_lat_game_offset=loc_lat_game_offset, 
                               map_api_key=map_api_key)
            
    else:

        return redirect("/")


####################################################################
# 
# REGISTER 
# Adapted from submitted solution to Finance problem
#
####################################################################
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        else:
            # Ensure password and confirmation match
            new_password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            if new_password == confirmation:
                new_username = request.form.get("username")
                new_password = generate_password_hash(confirmation)
                try:
                    queries.get_registered(db_pg, new_username, new_password)
                except (ValueError, RuntimeError):
                    return apology("username is already taken", 400)
                return redirect("/")
            else:
                return apology("password did not match", 400)
            
    else:

        if new_registrations:

            # Ensure session page is set to "register" before register.html is rendered
            session["page"] = "register"

            return render_template("register.html", 
                                page="register", 
                                map_api_key=map_api_key,
                                button="bttn-primary",
                                new_registrations=new_registrations)
        
        else:

            return redirect("/")


####################################################################
# 
# LOGIN
# Adapted from Finance template
#
####################################################################
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = queries.get_user_info(db_pg, request.form.get("username"))

        # Ensure username exists and password is correct
        if user:
            if not check_password_hash(user["hash"], request.form.get("password")):
                return apology("invalid username and/or password", 403)
        else:
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["status"] = user["status"]

        # Redirect user to home page
        return redirect("/")
    
    else:
        # Ensure session page is set to "login" before login.html is rendered
        session["page"] = "login"

        return render_template("login.html", 
                               page="login", 
                               map_api_key=map_api_key,
                               new_registrations=new_registrations)
    

####################################################################
# 
# LOGOUT function unchaged from Finance template
#
####################################################################
@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


####################################################################
#
# TRAFFIC
#
####################################################################
@app.route("/traffic", methods=["GET", "POST"])
def traffic():

    page = session["current_page"] = request.form.get("page")
    goto = session["current_goto"] = request.form.get("goto")

    try:
        try_again = session["try_again"] = request.form.get("try-again")
    except KeyError:
        try_again = session["try_again"] = 0

    # Set current_game_loc_id if Try Again clicked from Search History page
    if request.form.get("try-again-loc-id"):
        try_again_loc_id = session["current_game_loc_id"] = request.form.get("try-again-loc-id")
    else:
        try_again_loc_id = 0

    if "current_game_id" not in session:
        session["current_game_id"] = 0

    if session.get("user_id") is None:
        return redirect("/tout")
    
    else:
        return redirect("/tin")


####################################################################
#
# TRAFFIC - OUT
#
####################################################################
@app.route("/tout", methods=["GET", "POST"])
def traffic_out():

    page = session["current_page"]
    goto = session["current_goto"]

    if request.method == "POST":

        return redirect("/")
    
    else:

        if (page != "game") or (page != "result"):

            if goto == "about":
                return redirect("/about")
            
            if goto == "howto":
                return redirect("/howto")
            
            if goto == "index":
                 return redirect("/")
            
            # Disabled if no user
            # if goto == "history":
            #     return redirect("/history")

            # Disabled if no user
            # if goto == "profile":
            #     return redirect("/profile")

            # if goto == "profile_fifty":
            #     return redirect("/profile/fifty")
            
            if goto == "register":
                return redirect("/register")
            
            if goto == "login":
                return redirect("/login")
            
            # Disabled if no user
            # if goto == "logout":
            #     return redirect("/logout")
        
        else:

            return redirect("/")
    

####################################################################
#
# TRAFFIC - IN
#
####################################################################
@app.route("/tin", methods=["GET", "POST"])
@login_required
def traffic_in():
    """Request from user for new location or to stop game"""

    page = session["current_page"]
    goto = session["current_goto"]

    if request.method == "POST":
    
        return redirect("/")

    else:

        if (page != "game") and (page != "result"):

            if (page == "history") and (goto == "game_again"):

                return redirect("/game")
            
            else:

                if goto == "about":
                    return redirect("/about")
                
                if goto == "howto":
                    return redirect("/howto")
                
                if goto == "locs":
                    return redirect("/locs")
                
                if goto == "admin":
                    return redirect("/admin")
                
                if goto == "admin_fifty":
                    return redirect("/admin/fifty")
                
                if goto == "admin_users":
                    return redirect("/admin/users")
                
                if goto == "admin_users_add":
                    return redirect("/admin/users/add")
                
                if goto == "index":
                    return redirect("/")
                 
                if goto == "profile":
                    return redirect("/profile")
                
                if goto == "profile_fifty":
                    return redirect("/profile/fifty")
                               
                if goto == "history":
                    return redirect("/history")

                if goto == "register":
                    return redirect("/register")
                
                # Not rendered if session has user_id
                # if goto == "login":
                #     return redirect("/login")
                
                if goto == "logout":
                    return redirect("/logout")
                
                return redirect("/")

        elif page == "game":

            # Set current game end time
            # TODO All times default to CST
            now = datetime.now()

            # Calculate time difference in seconds
            duration_sec, duration_min = queries.game_answer_duration(session["current_game_start"], now)

            # Set update_current_game arguments
            id = session["current_game_id"] 
            game_end = now
            game_lat = None
            game_lng = None
            game_user_quit = 1
            game_answer_off = None
            # game_answer_validation = 0
            game_duration = duration_sec
            game_score = 0

            updates = {
                "id": session["current_game_id"], 
                "game_end": now,
                "game_lat": None,
                "game_lng": None,
                "game_user_quit": 1,
                "game_answer_off": None,
                "game_answer_validation": 0,
                "game_duration": duration_sec,
                "game_score": game_score
            }

            if goto == "zero":

                # Current game location abandoned and NO longer playable in future games
                updates["game_answer_validation"] = 2

                # Update record
                queries.update_current_game(db_pg, updates)

                # After game record has been updated, redirect to start new game location
                return redirect("/result")

            else:

                # TODO: Decide on duration seconds
                if duration_sec >= 10:
                    # If user is on game page for x sec or more, counted as an attempt
                    # Update record
                    queries.update_current_game(db_pg, updates)

                elif duration_sec >= 0:
                    # If user is on game page for under x sec, not counted as an attempt
                    # Delete record
                    queries.get_current_game_deleted(db_pg, id)

                else:
                    # Else redirect to index
                    # TODO: Better to redirect to error page
                    return redirect("/")

                # Ensure current_game_loc_id is cleared
                session.pop("current_game_loc_id", None)

                # After game record has been updated or deleted, redirect to requested page

                if goto == "game":
                    return redirect("/game")
            
                if goto == "about":
                    return redirect("/about")
                
                if goto == "howto":
                    return redirect("/howto")
                
                if goto == "locs":
                    return redirect("/locs")
                
                if goto == "admin":
                    return redirect("/admin")
                
                if goto == "admin_fifty":
                    return redirect("/admin/fifty")
                
                if goto == "admin_users":
                    return redirect("/admin/users")
                
                if goto == "admin_users_add":
                    return redirect("/admin/users/add")
                
                if goto == "index":
                    return redirect("/")

                if goto == "profile":
                    return redirect("/profile")
                
                if goto == "profile_fifty":
                    return redirect("/profile/fifty")
                                
                if goto == "history":
                    return redirect("/history")
                
                if goto == "logout":
                    return redirect("/logout")
                
                return redirect("/")

        elif page == "result":

            # If user "Quit Game", redirects to index
            # No current game to close
            
            if goto == "game_again":
                session["try_again"] = 1
                return redirect("/game")

            if goto == "zero":
                return redirect("/")
            
            if goto == "game_new":
                return redirect("/game")
            
            if goto == "about":
                return redirect("/about")
            
            if goto == "howto":
                return redirect("/howto")
            
            if goto == "locs":
                return redirect("/locs")
            
            if goto == "admin":
                    return redirect("/admin")
            
            if goto == "admin_fifty":
                    return redirect("/admin/fifty")
            
            if goto == "admin_users":
                    return redirect("/admin/users")
            
            if goto == "admin_users_add":
                    return redirect("/admin/users/add")
            
            if goto == "index":
                return redirect("/")

            if goto == "profile":
                return redirect("/profile")
            
            if goto == "profile_fifty":
                return redirect("/profile/fifty")
                        
            if goto == "history":
                return redirect("/history")
            
            if goto == "logout":
                return redirect("/logout")
            
            return redirect("/")

        else:
            return redirect("/")
        
