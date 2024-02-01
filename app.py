import os
import json
from datetime import datetime, timezone
import pytz
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import shapely.wkb
from shapely.geometry import Point

from helpers import apology, login_required, get_duration, get_distance, latitude_offset
from queries import get_registered, get_user_info, get_loc_duration_total, get_disconnected
import game_geo
import game_fifty
import game_dash


# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# View HTML changes without rerunning server
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure session
app.config["SESSION_PERMANENT"] = True
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


@app.route('/disconnect', methods=['POST'])
def disconnect_fifty():

    data = json.loads(request.data)
    message = data['message']

    if message == "8dc4ed2b-4e99-45f7-a6a2-319ccb31d17d":

        current_game_id = session["get_fifty_game_active"]["fifty_game_id"]
        current_game_start = session["get_fifty_game_active"]["fifty_game_start"]

        result = get_disconnected(db_pg, 
                                  current_game_id, 
                                  current_game_start)

        return '', 200

    else:

        return '', 200


@app.route('/disconnect/geofinder', methods=['POST'])
def disconnect_geofinder():

    data = json.loads(request.data)
    message = data['message']

    if message == "8dc4ed2b-4e99-45f7-a6a2-319ccb31d17d":
        current_game_id = session["get_geo_game_active"]["geo_game_id"]
        current_game_start = session["get_geo_game_active"]["geo_game_start"]

        result = get_disconnected(db_pg, 
                                  current_game_id, 
                                  current_game_start)

        return '', 200

    else:

        return '', 200
    
####################################################################
# 
# START
#
####################################################################
@app.route("/", methods=["GET", "POST"])
@login_required
def game__start():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "index"):

            if (nav == "no"):

                if (bttn == "start") or (bttn == "again"):

                    # Get today's geofinder
                    location = game_geo.get_geo_today_location_info(db_pg)

                    # Check if user has found or quit today's geofinder
                    geo_game_id = game_geo.get_geo_today_location_status(db_pg, 
                                                                                session["user_id"],
                                                                                location["geofinder_id"])

                    # ########################################################
                    # Player has NOT FOUND or QUIT today's geofinder
                    # ########################################################
                    if geo_game_id["geo_game_id"] == 0:

                        # Create new entry in geofinder_games table
                        new_geo_game_id = game_geo.get_geo_game_created(db_pg,
                                                                            session["user_id"], 
                                                                            location["geofinder_id"])

                        # Get current_geo_game saved to db to render on geofinder_game.html
                        new_geo_game = game_geo.get_geo_game_started(db_pg,
                                                                            new_geo_game_id)

                        # Get offset latitude to position infowindow on map
                        loc_lat_game_offset = latitude_offset(float(new_geo_game["loc_view_lat"]), 
                                                              float(new_geo_game["loc_view_lng"]))

                        # Clear package
                        session.pop("get_geo_game_active", None)

                        # Set GAME package
                        get_geo_game_active = {
                            "geo_game_id": new_geo_game_id,
                            "geo_game_start": new_geo_game["geo_game_start"],
                            "geo_game_geofinder_id": new_geo_game["geofinder_id"],
                            "geo_game_geofinder_date": new_geo_game["geofinder_date"], #.strftime('%a, %B %d')
                            "geo_game_loc_id": new_geo_game["id"],
                            "geo_game_loc_url_source": new_geo_game["loc_url_source"],
                            "geo_game_loc_view_lat": new_geo_game["loc_view_lat"],
                            "geo_game_loc_view_lng": new_geo_game["loc_view_lng"],
                            "geo_game_loc_key_shp": new_geo_game["loc_key_shp"],
                            "geo_game_loc_image_source": new_geo_game["loc_image_source"],
                            "geo_game_loc_city": new_geo_game["loc_city"],
                            "geo_game_loc_state": new_geo_game["loc_state"],
                            "geo_game_loc_country": new_geo_game["loc_country"],
                            "geo_game_loc_lat_game_offset": loc_lat_game_offset
                        }

                        # Save GAME package to Session
                        session["get_geo_game_active"] = get_geo_game_active
                    
                        return redirect("/geofinder/game")
                    
                    # ########################################################
                    # Player has FOUND or QUIT today's geofinder
                    # ########################################################    
                    else:

                        session.pop("get_geo_game_review", None)

                        review = location["geofinder_id"]

                        get_geo_game_review = game_geo.get_geo_game_reviewed(db_pg,
                                                                                    session["user_id"],
                                                                                    review)

                        # Save REVIEW package to Session
                        session["get_geo_game_review"] = get_geo_game_review

                        return redirect("/geofinder/review")
        
                else:

                    return redirect("/")
                
            elif (nav == "yes"):

                # Clean up session variables
                session.pop("get_geo_game_active", None)
                session.pop("get_geo_game_results", None)
                session.pop("get_geo_game_review", None)

                return redirect("/nav")
            
            else:

                return apology("wrong page", 403)

        else:

            return apology("wrong page", 403)
        
    else:

        return render_template("game_start.html", 
                               action="/",
                               page="index", 
                               map_api_key=map_api_key,
                               new_registrations=new_registrations)


####################################################################
# 
# GEOFINDER - GAME
#
####################################################################
@app.route("/geofinder/game", methods=["GET", "POST"])
@login_required
def game__geofinder_game():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "geofinder_game"):

            # Get GAME package from Session
            get_geo_game_active = session["get_geo_game_active"]

            # Set RESULTS package
            get_geo_game_results = {
                "geo_game_id": get_geo_game_active["geo_game_id"],
                "geo_game_geofinder_id": get_geo_game_active["geo_game_geofinder_id"],
                "geo_game_geofinder_date": get_geo_game_active["geo_game_geofinder_date"],
                "geo_game_start": get_geo_game_active["geo_game_start"],
                "geo_game_end": None,
                "geo_game_loc_id": get_geo_game_active["geo_game_loc_id"],
                "geo_game_loc_url_source": get_geo_game_active["geo_game_loc_url_source"],
                "geo_game_loc_view_lat": get_geo_game_active["geo_game_loc_view_lat"],
                "geo_game_loc_view_lng": get_geo_game_active["geo_game_loc_view_lng"],
                "geo_game_loc_key_shp": get_geo_game_active["geo_game_loc_key_shp"],
                "geo_game_loc_image_source": get_geo_game_active["geo_game_loc_image_source"],
                "geo_game_loc_city": get_geo_game_active["geo_game_loc_city"],
                "geo_game_loc_state": get_geo_game_active["geo_game_loc_state"],
                "geo_game_loc_country": get_geo_game_active["geo_game_loc_country"],
                "geo_game_loc_lat_game_offset": get_geo_game_active["geo_game_loc_lat_game_offset"],
                "geo_game_submit": 0,
                "geo_game_submit_lat": None,
                "geo_game_submit_lng": None,
                "geo_game_submit_off": None,
                "geo_game_submit_validation": 0,
                "geo_game_duration_display": None,
                "geo_game_score_base_display": 0,
                "geo_game_score_bonus_display": 0,
                "geo_game_score_total_display": 0,
            }

            # Set current game end time
            results_geo_game_end = get_geo_game_results["geo_game_end"] = datetime.now()

            # Calcuate game duration in minutes
            results_duration = get_geo_game_results["geo_game_duration_display"] = get_duration(get_geo_game_results["geo_game_start"], 
                                                                                               results_geo_game_end)

            if (nav == "no"):

                if (bttn == "submit"):

                    # Update RESULTS package
                    get_geo_game_results["geo_game_submit"] = 1
                    get_geo_game_results["geo_game_submit_lat"] = float(request.form.get("submit-lat"))
                    get_geo_game_results["geo_game_submit_lng"] = float(request.form.get("submit-long"))

                    # Convert the PostGIS geometry into a Shapely geometry object
                    polygon = shapely.wkb.loads(get_geo_game_results["geo_game_loc_key_shp"], hex=True)

                    # Create a point object from user submitted (lat, lng)
                    point = Point([get_geo_game_results["geo_game_submit_lng"], 
                                get_geo_game_results["geo_game_submit_lat"]])

                    # Update RESULTS package
                    get_geo_game_results["geo_game_submit_off"] = get_distance(point, polygon)

                    # Check if point is inside polygon
                    is_inside = polygon.contains(point)

                    # Validate answer as 1 = "correct"
                    if is_inside:

                        get_geo_game_results["geo_game_submit_validation"] = 1

                        # TODO Calculate scores
                        get_geo_game_results["geo_game_score_base_display"] = 555
                        get_geo_game_results["geo_game_score_bonus_display"] = 555
                        get_geo_game_results["geo_game_score_total_display"] = 555

                    # # Update geofinder_games table
                    game_geo.get_geo_game_updated(db_pg, get_geo_game_results)

                    # Update n1
                    session["n1"] = game_dash.get_dash_kpi_geofinder(db_pg, session["user_id"])

                    # Save RESULTS package to Session
                    session["get_geo_game_results"] = get_geo_game_results

                    return redirect("/geofinder/result")

                elif (bttn == "pause"):

                    if results_duration >= 10:

                        # If user is on geofinder_game page for 10 sec or more
                        # Update record
                        game_geo.get_geo_game_updated(db_pg, get_geo_game_results)

                        return redirect("/")

                    elif results_duration >= 0:

                        # If user is on geofinder_game page for under 10 sec
                        # Delete record
                        game_geo.get_geo_game_deleted(db_pg, get_geo_game_results["geo_game_id"])

                        return redirect("/")

                    else:

                        # Else redirect to index
                        # TODO: Better to redirect to error page
                        return redirect("/")

                elif (bttn == "quit"):

                    # Update RESULTS package
                    get_geo_game_results["geo_game_submit_validation"] = 2

                    # Update geofinder game record
                    game_geo.get_geo_game_updated(db_pg, get_geo_game_results)

                    # Update RESULTS package
                    get_geo_game_results["geo_game_submit_lat"] = get_geo_game_results["geo_game_loc_view_lat"]
                    get_geo_game_results["geo_game_submit_lng"] = get_geo_game_results["geo_game_loc_view_lng"]

                    # Save RESULTS package to Session
                    session["get_geo_game_results"] = get_geo_game_results

                    return redirect("/geofinder/result")

                else:
                    return redirect("/")

            elif (nav == "yes"):

                # NOTE: Clicking any navbar links is like clicking pause button

                if results_duration >= 10:

                    game_geo.get_geo_game_updated(db_pg, get_geo_game_results)

                elif results_duration >= 0:

                    game_geo.get_geo_game_deleted(db_pg, get_geo_game_results["geo_game_id"])

                else:

                    pass
                
                # Clean up session variables
                session.pop("get_geo_game_active", None)
                session.pop("get_geo_game_results", None)

                return redirect("/nav")

            else:

                return redirect("/")
    
        else:

            return redirect("/")
        
    else:

        # Get GAME package from session
        try:
            get_geo_game_active = session["get_geo_game_active"]        
        except:
            return redirect("/")

        return render_template("game_geo_game.html", 
                               action="/geofinder/game",
                               page="geofinder_game", 
                               map_api_key=map_api_key,
                               get_geo_game_active=get_geo_game_active)


####################################################################
#
# GEOFINDER - RESULT
#
####################################################################
@app.route("/geofinder/result", methods=["GET", "POST"])
@login_required
def game__geofinder_result():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "geofinder_result"):
        
            if (nav == "no"):

                if (bttn == "review"):

                    session.pop("geofinder_review", None)

                    review = request.form.get("review")

                    get_geo_game_review = game_geo.get_geo_game_reviewed(db_pg,
                                                                                session["user_id"],
                                                                                review)

                    session["get_geo_game_review"] = get_geo_game_review

                    return redirect("/geofinder/review")
                
                elif (bttn == "again"):

                    session.pop("get_geo_game_results", None)

                    return redirect("/geofinder/game")
                
                elif (bttn == "pause"):

                    session.pop("get_geo_game_results", None)

                    return redirect("/dash")
                
                elif (bttn == "quit"):

                    get_geo_game_results = session["get_geo_game_results"]

                    # Update RESULTS package
                    get_geo_game_results["geo_game_submit_validation"] = 2

                    # # Update geofinder game record
                    game_geo.get_geo_game_updated(db_pg, get_geo_game_results)

                    # # Update get_geo_game_results variables
                    # get_geo_game_results["geo_game_submit_lat"] = get_geo_game_results["geo_game_loc_view_lat"]
                    # get_geo_game_results["geo_game_submit_lng"] = get_geo_game_results["geo_game_loc_view_lng"]

                    # Save updated RESULT package to Session
                    session["get_geo_game_results"] = get_geo_game_results

                    return redirect("/geofinder/result")
                
                else:

                    return redirect("/")
            
            elif (nav == "yes"):

                # Clean up session variables
                session.pop("get_geo_game_active", None)
                session.pop("get_geo_game_results", None)

                return redirect("/nav")
            
            else:

                return redirect("/")
        
        else:

            return redirect("/")
            
    else:

        try:
            get_geo_game_results = session["get_geo_game_results"]
        except:
            return redirect("/")

        return render_template("game_geo_result.html", 
                               action="/geofinder/result",
                               page="geofinder_result", 
                               map_api_key=map_api_key,
                               get_geo_game_results=get_geo_game_results)


####################################################################
# 
# GEOFINDER - REVIEW
#
####################################################################
@app.route("/geofinder/review", methods=["GET", "POST"])
@login_required
def game__geofinder_review():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "geofinder_review"):

            if (nav == "no"):

                return redirect("/")
            
            elif (nav == "yes"):

                # Clean up session variables
                session.pop("get_geo_game_active", None)
                session.pop("get_geo_game_results", None)
                session.pop("get_geo_game_review", None)

                return redirect("/nav")
            
            else:

                return redirect("/")

        else:
            
            return redirect("/")
            
    else:

        try:
            get_geo_game_review = session["get_geo_game_review"]
        except:
            return redirect("/dash/geofinder")
        
        return render_template("game_geo_review.html", 
                               action="/geofinder/review",
                               page="geofinder_review",
                               map_api_key=map_api_key,
                               get_geo_game_review=get_geo_game_review)
    

####################################################################
# 
# FIFTY - START
#
####################################################################
@app.route("/fifty", methods=["GET", "POST"])
@login_required
def game__fifty_start():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        nav = request.form.get("nav")
        bttn = request.form.get("bttn")

    else:

        page = session["current_page"]
        goto = session["current_goto"]
        nav = session["current_nav"]
        bttn = session["current_bttn"]

    if (goto == "fifty_start"):

        if (nav == "no"):

            # Initiate GAME package
            get_fifty_game_active = {
                "fifty_game_id": None,
                "fifty_game_loc_id": None,
                "fifty_game_start": None,
                "fifty_game_loc_url_source": None,
                "fifty_game_loc_view_lat": None,
                "fifty_game_loc_view_lng": None,
                "fifty_game_loc_key_lat": None,
                "fifty_game_loc_key_lng": None,
                "fifty_game_loc_key_shp": None,
                "fifty_game_loc_image_source": None,
                "fifty_game_loc_city": None,
                "fifty_game_loc_state": None,
                "fifty_game_loc_country": None,
                "fifty_game_loc_lat_game_offset": None,
                "fifty_game_clock": None,
            }

            if (bttn == "again"):

                # Get specific location to try again
                loc_id_again = request.form.get("loc")

                location = game_fifty.get_fifty_playable_location_again(db_pg, 
                                                                        loc_id_again)
                
            else:

                # Get random location as new game
                location = game_fifty.get_fifty_playable_location(db_pg, 
                                                                  session["user_id"])

            # Checks if query returns a playable location
            if location == None:

                page = session["current_page"]
                goto = session["current_goto"] = "dash_fifty"
                nav = session["current_nav"]
                bttn = session["current_bttn"] = "dash_fifty"

                return redirect("/dash")
            else:
                # Update GAME package
                get_fifty_game_active["fifty_game_loc_id"] = location["id"]
                get_fifty_game_active["fifty_game_loc_key_shp"] = location["loc_key_shp"]
                get_fifty_game_active["fifty_game_loc_key_lat"] = location["loc_key_lat"]
                get_fifty_game_active["fifty_game_loc_key_lng"] = location["loc_key_lng"]

            # Create new entry in games table
            game_id, game_start = game_fifty.get_fifty_game_started(db_pg, 
                                                                    session["user_id"], 
                                                                    location["id"])
            
            # Get hour, minute and seconds from current_game_start
            clock = {
                "hour": game_start.hour,
                "minute": game_start.minute,
                "second": game_start.second
            }

            # Update GAME package
            get_fifty_game_active["fifty_game_id"] = game_id
            get_fifty_game_active["fifty_game_start"] = game_start
            get_fifty_game_active["fifty_game_loc_url_source"] = location["loc_url_source"]
            get_fifty_game_active["fifty_game_loc_view_lat"] = location["loc_view_lat"]
            get_fifty_game_active["fifty_game_loc_view_lng"] = location["loc_view_lng"]
            get_fifty_game_active["fifty_game_loc_image_source"] = location["loc_image_source"]
            get_fifty_game_active["fifty_game_loc_city"] = location["loc_city"]
            get_fifty_game_active["fifty_game_loc_state"] = location["loc_state"]
            get_fifty_game_active["fifty_game_loc_country"] = location["loc_country"]
            get_fifty_game_active["fifty_game_clock"] = clock

            # Get offset latitude to position infowindow on map
            loc_lat_game_offset = latitude_offset(float(location["loc_view_lat"]), 
                                                  float(location["loc_view_lng"]))
            
            # Update GAME package
            get_fifty_game_active["fifty_game_loc_lat_game_offset"] = loc_lat_game_offset

            # Save GAME package to Session
            session["get_fifty_game_active"] = get_fifty_game_active

            return redirect("/fifty/game")
        
        elif (nav == "yes"):

            return redirect("/")
        
        else:

            return redirect("/")

    else:

        redirect("/")


####################################################################
# 
# FIFTY - GAME
#
####################################################################
@app.route("/fifty/game", methods=["GET", "POST"])
@login_required
def game__fifty_game():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "fifty_game"):

            # Retrieve get_geofinder_game from session
            get_fifty_game_active = session["get_fifty_game_active"]

            # Set package
            get_fifty_game_results = {
                "fifty_game_id": get_fifty_game_active["fifty_game_id"],
                "fifty_game_start": get_fifty_game_active["fifty_game_start"],
                "fifty_game_end": None,
                "fifty_game_loc_id": get_fifty_game_active["fifty_game_loc_id"],
                "fifty_game_loc_url_source": get_fifty_game_active["fifty_game_loc_url_source"],
                "fifty_game_loc_view_lat": get_fifty_game_active["fifty_game_loc_view_lat"],
                "fifty_game_loc_view_lng": get_fifty_game_active["fifty_game_loc_view_lng"],
                "fifty_game_loc_key_shp": get_fifty_game_active["fifty_game_loc_key_shp"],
                "fifty_game_loc_image_source": get_fifty_game_active["fifty_game_loc_image_source"],
                "fifty_game_loc_city": get_fifty_game_active["fifty_game_loc_city"],
                "fifty_game_loc_state": get_fifty_game_active["fifty_game_loc_state"],
                "fifty_game_loc_country": get_fifty_game_active["fifty_game_loc_country"],
                "fifty_game_loc_lat_game_offset": get_fifty_game_active["fifty_game_loc_lat_game_offset"],
                "fifty_game_submit": 0,
                "fifty_game_submit_lat": None,
                "fifty_game_submit_lng": None,
                "fifty_game_submit_off": None,
                "fifty_game_submit_validation": 0,
                "fifty_game_submit_attempts": None,
                "fifty_game_duration_display": None,
                "fifty_game_duration_total_display": None,
                "fifty_game_score_base_display": 0,
                "fifty_game_score_bonus_display": 0,
                "fifty_game_score_total_display": 0,
            }

            # Get current game end time
            game_end = datetime.now(timezone.utc).astimezone(pytz.timezone('US/Central'))

            # Calcuate game duration in minutes
            game_duration = get_duration(get_fifty_game_results["fifty_game_start"], game_end)

            # Calcuate game duration for all previous attempts in minutes
            duration_total = get_loc_duration_total(db_pg, 
                                                    get_fifty_game_results["fifty_game_id"], 
                                                    session["user_id"], 
                                                    get_fifty_game_results["fifty_game_loc_id"], 
                                                    game_duration)

            # Update package
            get_fifty_game_results["fifty_game_end"] = game_end
            get_fifty_game_results["fifty_game_duration_display"] = game_duration
            get_fifty_game_results["fifty_game_duration_total_display"] = duration_total

            if (nav == "no"):

                if (bttn == "submit"):

                    # Update package
                    get_fifty_game_results["fifty_game_submit"] = 1
                    get_fifty_game_results["fifty_game_submit_lat"] = float(request.form.get("submit-lat"))
                    get_fifty_game_results["fifty_game_submit_lng"] = float(request.form.get("submit-long"))

                    # Convert the PostGIS geometry into a Shapely geometry object
                    polygon = shapely.wkb.loads(get_fifty_game_results["fifty_game_loc_key_shp"], hex=True)

                    # Create a point object from user submitted (lat, lng)
                    point = Point([get_fifty_game_results["fifty_game_submit_lng"], 
                                   get_fifty_game_results["fifty_game_submit_lat"]])

                    # Update package
                    get_fifty_game_results["fifty_game_submit_off"] = get_distance(point, polygon)

                    # Check if point is inside polygon
                    is_inside = polygon.contains(point)

                    # Validate answer as 1 = "correct"
                    if is_inside:

                        get_fifty_game_results["fifty_game_submit_validation"] = 1
                        
                    # Calculate game score
                    scores = game_fifty.get_fifty_game_score(db_pg, 
                                                             session["user_id"], 
                                                             get_fifty_game_results["fifty_game_loc_id"], 
                                                             get_fifty_game_results["fifty_game_submit_validation"], 
                                                             duration_total)
                    
                    # Update package
                    get_fifty_game_results["fifty_game_score_base_display"] = scores["base"]
                    get_fifty_game_results["fifty_game_score_bonus_display"] = scores["bonus"]
                    get_fifty_game_results["fifty_game_score_total_display"] = scores["total"]
                    get_fifty_game_results["fifty_game_submit_attempts"] = scores["attempts"]

                    # Update games table
                    game_fifty.get_fifty_game_updated(db_pg, get_fifty_game_results)

                    # Update n2
                    session["n2"] = game_dash.get_dash_kpi_fifty(db_pg, session["user_id"])

                    # For GET "/geofinder/results" to render in "geofinder.results.html"
                    session["get_fifty_game_results"] = get_fifty_game_results

                    return redirect("/fifty/result")
    
                elif (bttn == "new") or (bttn == "stop"):

                    if game_duration >= 10:

                        # If user is on fifty_game page for 10 sec or more
                        # Update record
                        game_fifty.get_fifty_game_updated(db_pg, get_fifty_game_results)

                    else:

                        # If user is on fifty_game page for under 10 sec
                        # Delete record
                        game_fifty.get_fifty_game_deleted(db_pg, get_fifty_game_results["fifty_game_id"])
                    
                    # Clear package from session
                    session.pop("get_fifty_game_results", None)

                    if (bttn == "new"):

                        return redirect("/fifty")
                    
                    elif (bttn == "stop"):

                        return redirect("/dash")

                    else:

                        return redirect("/")
                
                elif (bttn == "quit"):

                    # Update get_geo_game_results variables
                    get_fifty_game_results["fifty_game_submit_validation"] = 2

                    # Update geofinder game record
                    game_fifty.get_fifty_game_updated(db_pg, get_fifty_game_results)

                    # Get number of attempts
                    scores = game_fifty.get_fifty_game_score(db_pg, 
                                                             session["user_id"], 
                                                             get_fifty_game_results["fifty_game_loc_id"], 
                                                             get_fifty_game_results["fifty_game_submit_validation"], 
                                                             duration_total)

                    # Update package
                    get_fifty_game_results["fifty_game_submit_lat"] = get_fifty_game_results["fifty_game_loc_view_lat"]
                    get_fifty_game_results["fifty_game_submit_lng"] = get_fifty_game_results["fifty_game_loc_view_lng"]
                    get_fifty_game_results["fifty_game_submit_attempts"] = scores["attempts"]

                    # Update n2
                    session["n2"] = game_dash.get_dash_kpi_fifty(db_pg, session["user_id"])

                    # For GET "/geofinder/results" to render in "geofinder.results.html"
                    session["get_fifty_game_results"] = get_fifty_game_results

                    return redirect("/fifty/result")

                else:

                    redirect("/")

            elif (nav == "yes"):
                
                if game_duration >= 10:

                    # If user is on fifty_game page for 10 sec or more
                    # Update record
                    game_fifty.get_fifty_game_updated(db_pg, get_fifty_game_results)

                else:

                    # If user is on fifty_game page for under 10 sec
                    # Delete record
                    game_fifty.get_fifty_game_deleted(db_pg, get_fifty_game_results["fifty_game_id"])
                
                # Clear package from session
                session.pop("get_fifty_game_results", None)

                return redirect("/nav")

            else:

                redirect("/")

        else:

            return redirect("/")
        
    else:
        
        try:
            get_fifty_game_active = session["get_fifty_game_active"]
        except:
            redirect("/")

        return render_template("game_fifty_game.html", 
                               action="/fifty/game",
                               page="fifty_game",
                               map_api_key=map_api_key,
                               get_fifty_game_active=get_fifty_game_active)


####################################################################
#
# FIFTY - RESULT
#
####################################################################
@app.route("/fifty/result", methods=["GET", "POST"])
@login_required
def game__fifty_result():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "fifty_result") or (page == "dash_fifty"):
        
            if (nav == "no"):

                if (bttn == "review"):

                    session.pop("get_fifty_game_review", None)

                    review = request.form.get("review")

                    get_fifty_game_review = game_fifty.get_fifty_game_reviewed(db_pg, 
                                                                     session["user_id"], 
                                                                     review)

                    session["get_fifty_game_review"] = get_fifty_game_review 

                    return redirect("/fifty/review")
                
                elif (bttn == "stop"):

                    session.pop("get_fifty_game_results", None)

                    return redirect("/dash")
                
                else:

                    return redirect("/")
            
            elif (nav == "yes"):

                # Clean up session variables
                session.pop("get_geo_game_active", None)
                session.pop("get_geo_game_results", None)

                return redirect("/nav")
            
            else:

                return redirect("/")
        
        else:

            return redirect("/")
            
    else:

        try:
            get_fifty_game_results = session["get_fifty_game_results"]
        except:
            return redirect("/")

        return render_template("game_fifty_result.html", 
                               action="/fifty/result",
                               page="fifty_result", 
                               map_api_key=map_api_key,
                               get_fifty_game_results=get_fifty_game_results)


####################################################################
# 
# FIFTY - REVIEW
#
####################################################################
@app.route("/fifty/review", methods=["GET", "POST"])
@login_required
def game__fifty_review():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "fifty_review"):

            if (nav == "no"):

                return redirect("/")
            
            elif (nav == "yes"):

                # Clean up session variables
                session.pop("get_fifty_game_active", None)
                session.pop("get_fifty_game_results", None)
                session.pop("get_fifty_game_review", None)

                return redirect("/nav")
            
            else:

                return redirect("/")

        else:
            
            return redirect("/")
            
    else:

        try:
            get_fifty_game_review = session["get_fifty_game_review"]
        except:
            return redirect("/dash/fifty")

        return render_template("game_fifty_review.html", 
                               action="/fifty/review",
                               page="fifty_review",
                               map_api_key=map_api_key,
                               get_fifty_game_review=get_fifty_game_review)
    

####################################################################
# 
# DASH - START
#
####################################################################
@app.route("/dash", methods=["GET", "POST"])
@login_required
def game__dash_start():

    if request.method == "POST":

        return redirect("/")
    
    else:

        page = session["current_page"]
        goto = session["current_goto"]
        nav = session["current_nav"]
        bttn = session["current_bttn"]

        if (bttn != "profile_username") and (bttn != "profile_country") and (bttn != "profile_hash"):

            session.pop("profile_message_username", None)
            session.pop("profile_message_country", None)
            session.pop("profile_message_password", None)

        # Get values from session
        try:
            userid = session["user_id"]
        except KeyError:
            return redirect("/")

        if (goto == "dash_geofinder") or (bttn == "dash_geofinder"):

            # Save HEADER and CONTENT packages to Session
            session["get_dash_geofinder_today"] = datetime.now().strftime('%Y-%m-%d')
            session["get_dash_geofinder_header"] = game_dash.get_dash_geofinder_header(db_pg, userid)
            session["get_dash_geofinder_content"] = game_dash.get_dash_geofinder_content(db_pg, userid)

            return redirect("/dash/geofinder")

        elif (goto == "dash_fifty") or (bttn == "dash_fifty"):

            # Save HEADER and CONTENT packages to Session
            session["get_dash_fifty_header"] = game_dash.get_dash_fifty_header(db_pg, userid) 
            session["get_dash_fifty_content"] = game_dash.get_dash_fifty_content(db_pg, userid)

            return redirect("/dash/fifty")
    
        elif (goto == "dash_main") or (bttn == "dash"):

            # Save HEADER and CONTENT packages to Session
            session["get_dash_main"] = game_dash.get_dash_main(db_pg, userid)
            session["get_dash_geofinder_header"] = game_dash.get_dash_geofinder_header(db_pg, userid)
            session["get_dash_fifty_header"] = game_dash.get_dash_fifty_header(db_pg, userid) 

            return redirect("/dash/main")

        else:

            return redirect("/")


####################################################################
# 
# DASH - MAIN
#
####################################################################
@app.route("/dash/main", methods=["GET", "POST"])
@login_required
def game__dash_main():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "dash_main"):

            if (nav == "no"):

                username = request.form.get("username")
                country = request.form.get("country")
                pass_old = request.form.get("pass_old")
                pass_new = request.form.get("pass_new")
                pass_again = request.form.get("pass_again")

                session.pop("profile_message_username", None)
                session.pop("profile_message_country", None)
                session.pop("profile_message_password", None)

                if (bttn == "profile_username"): 

                    if username:
                        results = game_dash.get_dash_main_updated_username(db_pg,
                                                                           username, 
                                                                           session["user_id"])
                        
                        if results == 1:
                            session["profile_message_username"] = "Username changed"
                            session["username"] = username

                    else:
                        session["profile_message_username"] = "Username not changed"

                if (bttn == "profile_country"): 

                    if country:
                        results = game_dash.get_dash_main_updated_country(db_pg, 
                                                                               country, 
                                                                               session["user_id"])
                        
                        if results == 1:
                            session["profile_message_country"] = "Country changed"
                    
                    else:
                        session["profile_message_country"] = "Country not changed"
                
                if (bttn == "profile_hash"): 

                    if pass_old:

                        user = get_user_info(db_pg, session["username"])

                        if len(user) < 1 or not check_password_hash(user["hash"], pass_old):
                            session["profile_message_password"] = "Wrong password"

                        if pass_new == pass_again:
                            new_password = generate_password_hash(pass_again)
                            try:
                                game_dash.get_dash_main_updated_hash(db_pg, new_password, session["user_id"])
                                session["profile_message_password"] = "New password saved"
                            except (ValueError, RuntimeError):
                                session["profile_message_password"] = "New password not saved"
                        else:
                            session["profile_message_password"] = "New password did not match"

                    else:
                        session["profile_message_password"] = "New password not saved"
                
                return redirect("/dash")
            
            elif (nav == "yes"):

                return redirect("/nav")
            
            else:

                return redirect("/")

        else:

            return redirect("/")
    
    else:

        try:
            main = session["get_dash_main"]
        except:
            return redirect("/")
        
        try:
            header_geofinder = session["get_dash_geofinder_header"]
            
        except:
            return redirect("/")
        
        try:
            header_fifty = session["get_dash_fifty_header"]
        except:
            return redirect("/")
        
        try:
            profile_message_username = session["profile_message_username"]
        except:
            profile_message_username = None
        
        try:
            profile_message_country = session["profile_message_country"]
        except:
            profile_message_country = None
        
        try:
            profile_message_password = session["profile_message_password"]
        except:
            profile_message_password = None

        return render_template("game_dash_main.html", 
                               action="/dash/main",
                               page="dash_main", 
                               map_api_key=map_api_key,
                               main=main,
                               header_geofinder=header_geofinder,
                               header_fifty=header_fifty,
                               profile_message_username=profile_message_username,
                               profile_message_country=profile_message_country,
                               profile_message_password=profile_message_password)


####################################################################
# 
# DASH - GEOFINDER
#
####################################################################
@app.route("/dash/geofinder", methods=["GET", "POST"])
@login_required
def game__dash_geofinder():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "dash_geofinder"):

            if (nav == "no"):

                if (bttn == "review"):

                    review = request.form.get("review")

                    get_geo_game_review = game_geo.get_geo_game_reviewed(db_pg,
                                                                         session["user_id"],
                                                                         review)

                    session["get_geo_game_review"] = get_geo_game_review

                    return redirect("/geofinder/review")
                
                elif (bttn == "dash") or (bttn == "dash_geofinder"):

                    return redirect("/dash")

                else:     
                
                    return redirect("/")
            
            elif (nav == "yes"):

                # Clean up session variables
                session.pop("get_geo_game_active", None)
                session.pop("get_geo_game_results", None)
                session.pop("get_geo_game_review", None)

                return redirect("/nav")
            
            else:

                return redirect("/")

        else:
            
            return redirect("/")
            
    else:

        try:
            today = session["get_dash_geofinder_today"]
            header = session["get_dash_geofinder_header"]
            content = session["get_dash_geofinder_content"]
        except:
            return redirect("/")
        
        return render_template("game_dash_geofinder.html", 
                               action="/dash/geofinder",
                               page="dash_geofinder", 
                               map_api_key=map_api_key,
                               today=today,
                               header=header,
                               content=content)
    

####################################################################
# 
# DASH - FIFTY
#
####################################################################
@app.route("/dash/fifty", methods=["GET", "POST"])
@login_required
def game__dash_fifty():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "dash_fifty"):

            if (nav == "no"):

                if (bttn == "review"):

                    session.pop("get_fifty_game_review", None)

                    review = request.form.get("review")

                    get_fifty_game_review = game_fifty.get_fifty_game_reviewed(db_pg, 
                                                                               session["user_id"], 
                                                                               review)

                    session["get_fifty_game_review"] = get_fifty_game_review 

                    return redirect("/fifty/review")

                elif (bttn == "dash") or (bttn == "dash_fifty"):

                    return redirect("/dash")
                
                else:     
                
                    return redirect("/")
            
            elif (nav == "yes"):

                # Clean up session variables
                session.pop("get_geo_game_active", None)
                session.pop("get_geo_game_results", None)
                session.pop("get_geo_game_review", None)

                return redirect("/nav")
            
            else:

                return redirect("/")

        else:
            
            return redirect("/")
    
    else:

        try:
            header = session["get_dash_fifty_header"]
            content = session["get_dash_fifty_content"]
        except:
            return redirect("/")

        return render_template("game_dash_fifty.html", 
                               action="/dash/fifty",
                               page="dash_fifty", 
                               map_api_key=map_api_key,
                               header=header,
                               content=content)


####################################################################
# 
# ABOUT
#
####################################################################
@app.route("/about", methods=["GET", "POST"])
def game__about():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        return redirect("/nav")
    
    else:

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
                            action="/about",
                            page="about", 
                            map_api_key=map_api_key,
                            new_registrations=new_registrations)


####################################################################
# 
# HOW TO PLAY
#
####################################################################
@app.route("/howto", methods=["GET", "POST"])
def game__howto():

    if request.method == "POST":

        session["current_page"] = request.form.get("page")
        session["current_goto"] = request.form.get("goto")
        session["current_nav"] = request.form.get("nav")
        session["current_bttn"] = request.form.get("bttn")

        return redirect("/nav")
    
    else:
        
        return render_template("howto.html", 
                               action="/howto",
                               page="howto", 
                               map_api_key=map_api_key,
                               new_registrations=new_registrations)


####################################################################
# 
# REGISTER 
#
####################################################################
@app.route("/register", methods=["GET", "POST"])
def game__register():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "register"):

            if (nav == "no"):

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

                        results = get_registered(db_pg, new_username, new_password)

                        if results != 1:
                            return apology("username is already taken", 400)
                        else:
                            return redirect("/")
                    
                    else:

                        return apology("password did not match", 400)
            
            elif (nav == "yes"):

                return redirect("/nav")
            
            else:

                return redirect("/")
        
        else:

            return redirect("/")
            
    else:

        if new_registrations:

            return render_template("register.html", 
                                   action="/register", 
                                   page="register", 
                                   map_api_key=map_api_key,
                                   button="bttn-primary",
                                   new_registrations=new_registrations)
        
        else:

            return redirect("/")


####################################################################
# 
# LOGIN
# Adapted from CS50x pset Finance 
#
####################################################################
@app.route("/login", methods=["GET", "POST"])
def game__login():

    page = session["current_page"] = request.form.get("page")
    goto = session["current_goto"] = request.form.get("goto")
    nav = session["current_nav"] = request.form.get("nav")
    bttn = session["current_bttn"] = request.form.get("bttn")
    
    if request.method == "POST":

        if (page == "login"):

            if (nav == "no"):

                if (bttn == "login"):

                    # Forget any user_id
                    session.clear()

                    # Ensure username was submitted
                    if not request.form.get("username"):
                        return apology("must provide username", 403)

                    # Ensure password was submitted
                    elif not request.form.get("password"):
                        return apology("must provide password", 403)

                    # Query database for username
                    user = get_user_info(db_pg, request.form.get("username"))

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
                    session["n1"] = game_dash.get_dash_kpi_geofinder(db_pg, user["id"])
                    session["n2"] = game_dash.get_dash_kpi_fifty(db_pg, user["id"])

                    # Redirect user to home page
                    return redirect("/")
                
                else:

                    redirect ("/")
            
            elif (nav == "yes"):

                return redirect("/nav")
            
            else:

                return redirect("/")
        
        else:

            return redirect("/")
    
    else:

        return render_template("login.html", 
                               action="/login",
                               page="login", 
                               map_api_key=map_api_key,
                               new_registrations=new_registrations)
    

####################################################################
# 
# Error
#
####################################################################
@app.route("/error", methods=["GET", "POST"])
def game__error():

    page = session["current_page"] = request.form.get("page")
    goto = session["current_goto"] = request.form.get("goto")
    nav = session["current_nav"] = request.form.get("nav")
    bttn = session["current_bttn"] = request.form.get("bttn")
    
    if request.method == "POST":

        if (page == "error"):

            if (nav == "no"):

                redirect ("/")
            
            elif (nav == "yes"):

                return redirect("/nav")
            
            else:

                return redirect("/")
        
        else:

            return redirect("/")

    else:

        error = session["error_message"]
        
        return render_template("game_error.html", 
                               action="/error",
                               page="error", 
                               map_api_key=map_api_key,
                               new_registrations=new_registrations,
                               error=error)
    

####################################################################
# 
# LOGOUT 
#
####################################################################
@app.route("/logout", methods=["GET", "POST"])
def game__logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

####################################################################
#
# NAVIGATION
#
####################################################################
@app.route("/nav", methods=["GET", "POST"])
def game__navigation():

    if request.method == "POST":
    
        return redirect("/")
    
    else:

        if session.get("user_id") is None:
            return redirect("/nav/out")
    
        else:
            return redirect("/nav/in")


####################################################################
#
# NAVIGATION - OUT
#
####################################################################
@app.route("/nav/out", methods=["GET", "POST"])
def game__navigation_out():

    if request.method == "POST":
    
        return redirect("/")
    
    else:

        page = session["current_page"]
        goto = session["current_goto"]
        nav = session["current_nav"]
        bttn = session["current_bttn"]

        if (nav == "no"):

            return redirect("/")
        
        elif (nav == "yes"):

            if (bttn == "about"):
                return redirect("/about")
            
            if (bttn == "howto"):
                return redirect("/howto")
            
            if (bttn == "register"):
                return redirect("/register")
            
            if (bttn == "login"):
                return redirect("/login")
            
            return redirect("/")
    
        else:
            
            return redirect("/")


####################################################################
#
# NAVIGATION - IN
#
####################################################################
@app.route("/nav/in", methods=["GET", "POST"])
@login_required
def game__navigation_in():

    if request.method == "POST":
    
        return redirect("/")
    
    else:

        page = session["current_page"]
        goto = session["current_goto"]
        nav = session["current_nav"]
        bttn = session["current_bttn"]

        if (nav == "yes"):

            # Redirect based on button - order left to right
            if (bttn == "about"):
                return redirect("/about")
            
            if (bttn == "howto"):
                return redirect("/howto")
            
            if (bttn == "index"):
                return redirect("/")
            
            if (bttn == "dash_geofinder"):
                return redirect("/dash")
            
            if (bttn == "dash_fifty"):
                return redirect("/dash")
            
            if (bttn == "dash"):
                return redirect("/dash")
            
            if (bttn == "logout"):
                return redirect("/logout")

            return redirect("/")
        
        else:

            return redirect("/")

