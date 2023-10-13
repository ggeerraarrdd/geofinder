import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, latitude_offset
import queries


# Configure application
app = Flask(__name__)

# View HTML changes without rerunning server
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set SQLite database
db = "geo.db"

# Make sure Google Maps API key is set
# In terminal window, execute: export MAP_API_KEY=value
#
if not os.environ.get("MAP_API_KEY"):
    # TO DELETE
    # map_api_key = "AIzaSyDnegNPWUO2qN9pMWUaW4fxcV1VGn64Tyc"
    print("INFO: MAP_API_KEY not set")
    print("INFO: Get a Google Maps API Key")
    print("INFO: On terminal, excecute: 'export MAP_API_KEY=value'")

    raise RuntimeError("MAP_API_KEY not set")
else:
    print("MAP_API_KEY set")
    map_api_key = os.environ.get("MAP_API_KEY")

# Set default number of active locations
default_map_lat = 0
default_map_long = 0


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


####################################################################
#
# INDEX
#
####################################################################
@app.route("/")
@login_required
def index():
    """Show homepage"""

    # Print to debug
    # print("INDEX() function call")

    # Calculate user total score
    session["user_total_score"] = queries.get_total_score(db, session["user_id"])

    # Ensure session page is set to index before index.html is rendered
    session.pop("page", None)
    session["page"] = "index"

    # Print to debug
    print(f"\nprint from app.py > index():\n{session}\n")

    return render_template("index.html", page="index", userid=session["user_id"], username=session["username"], total=session["user_total_score"], map_api_key=map_api_key)


####################################################################
#
# GAME
#
####################################################################
@app.route("/game", methods=["GET", "POST"])
@login_required
def game():
    """Start a game"""
    
    # Printo to debug
    print("GAME() function call")

    if "try_again" not in session:
        session["try_again"] = 0

    # Printo to debug
    print(f"Try Again: {session['try_again']}")

    # Print to debug
    print(f"\nPre-gane session check - BEFORE clean-up: \n{session}\n")

    # Clean-up session
    # Leave only user_id and username
    # And current_game_loc_id - will be cleared if user starts new game
    session.pop("current_game_id", None)
    session.pop("current_game_lat_default", None)
    session.pop("current_game_long_default", None)
    session.pop("current_game_lat_answer_key", None)
    session.pop("current_game_long_answer_key", None)
    session.pop("current_game_lat_answer_user", None)
    session.pop("current_game_long_answer_user", None)
    session.pop("current_game_start", None)
    session.pop("current_game_map_center", None)
    session.pop("current_game_map_zoom", None)

    # Print to debug
    print(f"\nPre-gane session check - AFTER clean-up: \n{session}\n")

    if session["try_again"] == 1:
        location = queries.get_playable_location_again(db, session["current_game_loc_id"])
    else:
        location = queries.get_playable_location(db, session["user_id"])

    # Update session with location info to be played
    session["current_game_loc_id"] = location["id"]
    session["current_game_lat_answer_key"] = location["loc_lat_key"]
    session["current_game_long_answer_key"] = location["loc_lng_key"]

    # Create new entry in games table
    current_game_id, current_game_start = queries.start_game(db, session["user_id"], session["current_game_loc_id"])
    
    # Get hour, minute and seconds from current_game_start
    clock = {
        "hour": current_game_start.hour,
        "minute": current_game_start.minute,
        "second": current_game_start.second
    }

    # Update session with game info to be played
    session["current_game_loc_id"] = location["id"]
    session["current_game_lat_default"] = location["loc_lat_game"]
    session["current_game_long_default"] = location["loc_lng_game"]
    session["current_game_lat_answer_key"] = location["loc_lat_key"]
    session["current_game_long_answer_key"] = location["loc_lng_key"]
    session["current_game_id"] = current_game_id
    session["current_game_start"] = current_game_start

    # Print to debug
    print(f"DATA SENT TO GAME PAGE: \n{location}\n")

    # Get offset latitude to position infowindow on map
    loc_lat_game_offset = latitude_offset(float(location["loc_lat_game"]), float(location["loc_lng_game"]))

    # Ensure session page is set to "game" before game.html is rendered
    session["page"] = "game"

    # Print to debug
    print(f"SESSION JUST BEFORE RENDER TEMPLATE: \n{session}\n")

    return render_template("game.html", page="game", username=session["username"], total=session["user_total_score"], location=location, loc_lat_game_offset=loc_lat_game_offset, clock=clock, map_api_key=map_api_key)


####################################################################
#
# RESULT
#
####################################################################
@app.route("/result", methods=["GET", "POST"])
@login_required
def result():
    """Submit game"""

    # Printo to debug
    # print("RESULT() function call")

    # Set current timestamp
    current_game_end = datetime.now()

    # Get user-submitted answer
    current_game_lat_answer_user = request.form.get("answer-lat")
    current_game_long_answer_user = request.form.get("answer-long")
    
    # Update session
    session["current_game_lat_answer_user"] = current_game_lat_answer_user
    session["current_game_long_answer_user"] = current_game_long_answer_user 
    session["current_game_map_center"] = request.form.get("answer-map-center")
    session["current_game_map_zoom"] = request.form.get("answer-map-zoom")

    # Get location answer 
    lat_answer_key = session["current_game_lat_answer_key"]
    long_answer_key = session["current_game_long_answer_key"]

    # Calculate distance difference between answer key and user submission
    game_answer_distance = queries.game_answer_distance(lat_answer_key, long_answer_key, current_game_lat_answer_user, current_game_long_answer_user)

    # Validate answer as 1 = "correct" or 0 = "incorrect"
    if game_answer_distance <= 40:
        game_answer_validation = 1
        current_game_answer_user_validation = "correct!"
    else:
        game_answer_validation = 0
        current_game_answer_user_validation = "incorrect."

    # Calcuate game duration in minutes
    durations = queries.game_answer_duration(session["current_game_start"], current_game_end)

    # Calcuate game duration for all previous attempts in minutes
    duration_total = queries.get_loc_duration_total(db, session["current_game_id"], session["user_id"], session["current_game_loc_id"], durations[1])

    # Calculate game score
    scores = queries.game_answer_score(db, session["user_id"], session["current_game_loc_id"], game_answer_validation, duration_total)
    base_score = scores[0]
    bonus_score = scores[1]
    game_score = scores[2]
    attempts = scores[3]

    # Print to debug
    # print(f"\nAnswer: ({current_game_lat_answer_user}, {current_game_long_answer_user})")
    # print(f"Distance: {game_answer_validation}")
    # print(f"Validation: {game_answer_validation}")
    # print(f"Duration: {durations}")
    # print(f"Base Score: {base_score}")
    # print(f"Bonus Score: {bonus_score}")
    # print(f"Score: {game_score}\n")

    # Set update_current_game arguments
    id = session["current_game_id"] 
    game_end = current_game_end
    game_lat = current_game_lat_answer_user
    game_lng = current_game_long_answer_user
    game_user_quit = 0
    game_answer_off = game_answer_distance
    # game_answer_validation = game_answer_validation
    game_duration = durations[1]
    # game_score = game_score

    # Update games table
    queries.update_current_game(db, id, game_end, game_lat, game_lng, game_user_quit, game_answer_off, game_answer_validation, game_duration, game_score)

    # Update session with new total score
    session["user_total_score"] = queries.get_total_score(db, session["user_id"])

    # Create dictionary for html page
    results = {
        "current_game_lat_default": session["current_game_lat_default"],
        "current_game_long_default": session["current_game_long_default"],
        "current_game_lat_answer_user": current_game_lat_answer_user,
        "current_game_long_answer_user": current_game_long_answer_user,
        "answer_validation": game_answer_validation,
        "current_game_answer_user_validation": current_game_answer_user_validation,
        "current_game_loc_id": session["current_game_loc_id"],
        "current_game_loc_attempt": attempts,
        "current_game_duration": game_duration,
        "current_location_duration": duration_total,
        "current_game_score_base": base_score,
        "current_game_score_bonus": bonus_score,
        "current_game_score_total": game_score
    }

    print(results)

    # Ensure session page is set to "result" before submit.html is rendered
    session["page"] = "result"

    return render_template("submit.html", data=results, page="result", username=session["username"], total=session["user_total_score"], map_api_key=map_api_key)


####################################################################
#
# ABOUT
#
####################################################################
@app.route("/about", methods=["GET", "POST"])
def about():
    """Get about page."""

    # Printo to debug
    # print("ABOUT() function call")

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
        total = session["user_total_score"]
    except KeyError:
        total = 0

    # Ensure session page is set to "about" before about.html is rendered
    session["page"] = "about"
    
    return render_template("about.html", page="about", userid=userid, username=username, total=total, map_api_key=map_api_key)


####################################################################
#
# HOW TO PLAY
#
####################################################################
@app.route("/howto", methods=["GET", "POST"])
def howto():
    """Get how to page"""

    # Print to debug
    # print("HOWTO() function call")

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
        total = session["user_total_score"]
    except KeyError:
        total = 0

    # Ensure session page is set to "howto" before howto.html is rendered
    session["page"] = "howto"
    
    return render_template("howto.html", page="howto", userid=userid, username=username, total=total, map_api_key=map_api_key)


####################################################################
#
# HISTORY
#
####################################################################
@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show user history of games """

    # Print to debug
    # print("HISTORY function call")

    history = queries.get_history(db, session["user_id"])

    # Printo to debug
    # print(history[0])

    # Ensure session page is set to "history" before history.html is rendered
    session["page"] = "history"

    return render_template("history.html", page="history", history=history, userid=session["user_id"], username=session["username"], total=session["user_total_score"], map_api_key=map_api_key)


####################################################################
#
# REGISTER function sourced from submitted solution to Finance problem
#
####################################################################
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Printo to debug
    # print("REGISTER function call")

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        else:
            new_password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            if new_password == confirmation:
                new_username = request.form.get("username")
                new_password = generate_password_hash(confirmation)
                try:
                    queries.get_user(db, new_username, new_password)
                except (ValueError, RuntimeError):
                    # Check error types at https://cs50.readthedocs.io/libraries/cs50/python/
                    return apology("username is already taken", 400)
                return redirect("/")
            else:
                return apology("password did not match", 400)
    else:

        # Ensure session page is set to "register" before register.html is rendered
        session["page"] = "register"

        return render_template("register.html", page="register", map_api_key=map_api_key)


####################################################################
#
# LOGIN
# Adapted from Finance template
#
####################################################################
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Print to debug
    # print("LOGIN() function call")

    # Forget any user_id
    session.clear()

    # Printo to debug
    # print("Session cleared")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = queries.get_user_info(db, request.form.get("username"))

        # Ensure username exists and password is correct
        if len(user) != 3 or not check_password_hash(user["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Ensure session page is set to "login" before login.html is rendered
        session["page"] = "game"

        return render_template("login.html", page="login", map_api_key=map_api_key)
    

####################################################################
#
# LOGOUT function unchaged from Finance template
#
####################################################################
@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""

    # Printo to debug
    # print("LOGOUT() function call")

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

    # Print to debug
    # print("TRAFFIC() function call")

    session["current_page"] = request.form.get("page")
    session["current_goto"] = request.form.get("goto")

    try:
        session["try_again"] = request.form.get("try-again")
    except KeyError:
        session["try_again"] = 0

    if "current_game_id" not in session:
        session["current_game_id"] = 0

    # Print to debug
    # print("\nTRAFFIC:")
    # print(f"Current Page: {session['current_page']}")
    # print(f"Request Go To: {session['current_goto']}")
    # print(f"Try Again: {session['try_again']}")
    # print(f"Current Game ID: {session['current_game_id']}\n")

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

    # Print to debug
    # print("TRAFIC_OUT() function call")

    page = session["current_page"]
    goto = session["current_goto"]

    # Print to debug
    # print("\nTRAFFIC OUT:")
    # print(f"Current Page: {session['current_page']}")
    # print(f"Request Go To: {session['current_goto']}")
    # print(f"Try Again: {session['try_again']}")
    # print(f"Current Game ID: {session['current_game_id']}\n")

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

    # Print to debug
    # print("ROUTER() / TRAFFIC_IN() function call")

    page = session["current_page"]
    goto = session["current_goto"]

    # Print to debug
    # print("\nTRAFFIC IN:")
    # print(f"page: {page}")
    # print(f"goto: {goto}")

    if request.method == "POST":
    
        return redirect("/")

    else:

        if (page != "game") and (page != "result"):

            # Print to debug
            # print("TRAFIC_IN() function call -> not GAME or not RESULT")

            # Print to debug
            # print("\nTRAFIC_IN() function call -> not GAME or not RESULT:")
            # print(f"page: {page}")
            # print(f"goto: {goto}")

            if goto == "about":
                return redirect("/about")
            
            if goto == "howto":
                return redirect("/howto")
            
            if goto == "index":
                return redirect("/")
            
            if goto == "history":
                return redirect("/history")
            
            # Not rendered if session has user_id
            # if goto == "register":
            #     return redirect("/register")
            
            # Not rendered if session has user_id
            # if goto == "login":
            #     return redirect("/login")
            
            if goto == "logout":
                return redirect("/logout")

        elif page == "game":

            # Print to debug
            # print("TRAFIC_IN() function call -> page GAME")

            # Print to debug
            # print("\nTRAFIC_IN() function call -> page GAME:")
            # print(f"page: {page}")
            # print(f"goto: {goto}")

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
            game_answer_validation = 0
            game_duration = duration_min
            game_score = 0

            # TODO: Decide on duration seconds
            if duration_sec >= 10:
                # If user is on game page for x sec or more, counted as an attempt
                # Update record
                queries.update_current_game(db, id, game_end, game_lat, game_lng, game_user_quit, game_answer_off, game_answer_validation, game_duration, game_score)

            elif duration_sec >= 0:
                # If user is on game page for under x sec, not counted as an attempt
                # Delete record
                queries.get_current_game_deleted(db, id)

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
            
            if goto == "index":
                return redirect("/")
            
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
            
            if goto == "game_new":
                return redirect("/game")
            
            if goto == "about":
                return redirect("/about")
            
            if goto == "howto":
                return redirect("/howto")
            
            if goto == "index":
                return redirect("/")
            
            if goto == "history":
                return redirect("/history")
            
            if goto == "logout":
                return redirect("/logout")
            
            return redirect("/")

        else:
            return redirect("/")