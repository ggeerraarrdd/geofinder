import os
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from queries import get_registered, get_user_info
# import game_geo
import game_fifty
import game_dash
# from pprint import pprint as pp


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

    
####################################################################
# 
# INDEX
#
####################################################################
@app.route("/", methods=["GET", "POST"])
@login_required
def game__index():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        nav = request.form.get("nav")
        bttn = request.form.get("bttn")

        if (page == "index"):

            # Start bttn temp direct to Geo50x
            if (bttn == "temp"):

                # Create FIFTY_PACKAGE_GAME package
                fifty_package_game = game_fifty.get_fifty_package_game(db_pg, 
                                                                    session["user_id"])

                # Save FIFTY_PACKAGE_GAME package to Session
                session["fifty_package_game"] = fifty_package_game

                return redirect("/fifty/game")

            else:

                return apology("wrong page", 403)

        else:

            return apology("wrong page", 403)
    else:

        return render_template("index.html", 
                               map_api_key=map_api_key,
                               new_registrations=new_registrations)


####################################################################
# 
# FIFTY - DASH
#
####################################################################
@app.route("/fifty/dash", methods=["GET", "POST"])
@login_required
def game__fifty_dash():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        nav = request.form.get("nav")
        bttn = request.form.get("bttn")

        if (page == "fifty_page_dash"):

            if (bttn == "review"):

                # Create new FIFTY_GAME_REVIEW package
                fifty_package_review = game_fifty.get_fifty_package_review(db_pg, 
                                                                           session["user_id"], 
                                                                           request.form.get("loc"),
                                                                           request.form.get("time"),
                                                                           request.form.get("score"))

                # Save FIFTY_GAME_REVIEW package to Session
                session["fifty_package_review"] = fifty_package_review 

                return redirect("/fifty/review")
            
            elif (bttn == "start"):

                # Create FIFTY_PACKAGE_GAME package
                fifty_package_game = game_fifty.get_fifty_package_game(db_pg, 
                                                                       session["user_id"])

                # Save FIFTY_PACKAGE_GAME package to Session
                session["fifty_package_game"] = fifty_package_game

                return redirect("/fifty/game")
            
            elif (bttn == "again"):

                # Create FIFTY_PACKAGE_GAME package
                fifty_package_game = game_fifty.get_fifty_package_game_again(db_pg, 
                                                                             session["user_id"],
                                                                             request.form.get("loc"))
                
                # Save FIFTY_PACKAGE_GAME package to Session
                session["fifty_package_game"] = fifty_package_game
            
                return redirect("/fifty/game")
            
            else:

                return redirect("/")
            
        else:

            return redirect("/")
    
    else:

        # Clean up session variables
        session.pop("fifty_package_game", None)
        session.pop("fifty_package_results", None)
        session.pop("fifty_package_review", None)

        try:
            header = session["fifty_package_dash_header"]
            content = session["fifty_package_dash_content"]
        except:
            return redirect("/")

        return render_template("game_fifty_dash.html", 
                               map_api_key=map_api_key,
                               header=header,
                               content=content)


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

        if (page == "fifty_page_game"):

            # Get FIFTY_PACKAGE_GAME from Session
            fifty_package_game = session["fifty_package_game"]

            # Clear FIFTY_PACKAGE_GAME in Session
            session.pop("fifty_package_game", None)

            if (bttn == "fifty_page_game_new") or (bttn == "fifty_page_game_pause"):

                if (bttn == "fifty_page_game_new"):

                    # Get new FIFTY_PACKAGE_GAME in Session
                    session["fifty_package_game"] = game_fifty.get_fifty_package_game(db_pg, 
                                                                                      session["user_id"])

                    return redirect("/fifty/game")
                
                elif (bttn == "fifty_page_game_pause"):

                    return redirect("/fifty/dash")

                else:

                    return redirect("/")

            elif (bttn == "fifty_page_game_quit") or (bttn == "fifty_page_game_submit"):

                if (bttn == "fifty_page_game_quit"):

                    # Get submit latlng
                    fifty_game_submit = 0
                    fifty_game_submit_lat = None
                    fifty_game_submit_lng = None
                    fifty_game_submit_lat_display = fifty_package_game["fifty_game_loc_key_lat"]
                    fifty_game_submit_lng_display = fifty_package_game["fifty_game_loc_key_lng"]

                elif (bttn == "fifty_page_game_submit"):

                    # Get submit latlng
                    fifty_game_submit = 1
                    fifty_game_submit_lat_display = fifty_game_submit_lat = float(request.form.get("submit-lat"))
                    fifty_game_submit_lng_display = fifty_game_submit_lng = float(request.form.get("submit-long"))
                
                else:

                    return redirect("/")

                # Get FIFTY_PACKAGE_RESULTS
                fifty_package_results = game_fifty.get_fifty_package_results(db_pg, 
                                                                             session["user_id"], 
                                                                             fifty_package_game,
                                                                             fifty_game_submit,
                                                                             fifty_game_submit_lat,
                                                                             fifty_game_submit_lng,
                                                                             fifty_game_submit_lat_display,
                                                                             fifty_game_submit_lng_display)

                # Update record
                game_fifty.get_fifty_game_updated(db_pg, fifty_package_results)

                # Update n2
                session["n2"] = game_fifty.get_fifty_kpi(db_pg, session["user_id"])

                # Update FIFTY_PACKAGE_DASH_HEADER and FIFTY_PACKAGE_DASH_CONTENT
                session["profile_package_fifty"] = session["fifty_package_dash_header"] = game_fifty.get_fifty_package_dash_header(db_pg, session["user_id"]) 
                session["fifty_package_dash_content"] = game_fifty.get_fifty_package_dash_content(db_pg, session["user_id"])

                # Save FIFTY_PACKAGE_RESULTS to Session
                session["fifty_package_results"] = fifty_package_results

                return redirect("/fifty/results")

            else:

                return redirect("/")
            
        else:

            return redirect("/")
        
    else:

        try:
            package = session["fifty_package_game"]
        except:
            return redirect("/fifty/dash")
        
        if package:

            return render_template("game_fifty_game.html", 
                                map_api_key=map_api_key,
                                package=package)
        
        else:

            return redirect("/fifty/dash")
        

####################################################################
#
# FIFTY - RESULTS
#
####################################################################
@app.route("/fifty/results", methods=["GET", "POST"])
@login_required
def game__fifty_results():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "fifty_page_results"):

            if (bttn == "review"):

                # Create new FIFTY_GAME_REVIEW
                fifty_package_review = game_fifty.get_fifty_package_review(db_pg, 
                                                                           session["user_id"], 
                                                                           request.form.get("loc"),
                                                                           request.form.get("time"),
                                                                           request.form.get("score"))

                # Save FIFTY_GAME_REVIEW to Session
                session["fifty_package_review"] = fifty_package_review 

                return redirect("/fifty/review")
            
            elif (bttn == "again"):

                try:
                    fifty_package_results = session["fifty_package_results"]
                except:
                    return redirect("/fifty/dash")
                
                if (fifty_package_results["fifty_game_submit_attempts"] < 6):

                    fifty_package_game = game_fifty.get_fifty_package_game_again(db_pg, 
                                                                                 session["user_id"],
                                                                                 request.form.get("loc"))
                    
                    session["fifty_package_game"] = fifty_package_game
                
                    return redirect("/fifty/game")
                
                else:

                    return redirect("/fifty/dash")

            elif (bttn == "new"):

                # Get new FIFTY_PACKAGE_GAME in Session
                session["fifty_package_game"] = game_fifty.get_fifty_package_game(db_pg,
                                                                                  session["user_id"])

                return redirect("/fifty/game")

            elif (bttn == "history"):

                return redirect("/fifty/dash")
            
            else:

                return redirect("/")
        
        else:

            return redirect("/")
            
    else:

        try:
            fifty_package_results = session["fifty_package_results"]
        except:
            return redirect("/")

        return render_template("game_fifty_result.html", 
                               action="/fifty/results",
                               page="fifty_page_results", 
                               map_api_key=map_api_key,
                               package=fifty_package_results)


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
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "fifty_page_review"):
            
            if (bttn == "new"):

                    # Get new FIFTY_PACKAGE_GAME in Session
                    session["fifty_package_game"] = game_fifty.get_fifty_package_game(db_pg, 
                                                                                      session["user_id"])

                    return redirect("/fifty/game")
            
            elif (bttn == "history"):

                return redirect("/fifty/dash")
            
            else:

                return redirect("/")

        else:
            
            return redirect("/")
            
    else:

        try:
            fifty_package_review = session["fifty_package_review"]
        except:
            return redirect("/fifty/dash")

        return render_template("game_fifty_review.html", 
                               map_api_key=map_api_key,
                               package=fifty_package_review)
    

####################################################################
# 
# PROFILE
#
####################################################################
@app.route("/profile", methods=["GET", "POST"])
@login_required
def game__profile():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        nav = session["current_nav"] = request.form.get("nav")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "dash_main"):

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

        else:

            return redirect("/")
    
    else:

        try:
            main = session["profile_package_main"]
            header_geofinder = None # session["profile_package_geo"]
            header_fifty = session["profile_package_fifty"]
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

        return render_template("profile.html", 
                               map_api_key=map_api_key,
                               main=main,
                               header_geofinder=header_geofinder,
                               header_fifty=header_fifty,
                               profile_message_username=profile_message_username,
                               profile_message_country=profile_message_country,
                               profile_message_password=profile_message_password)


####################################################################
# 
# ABOUT
#
####################################################################
@app.route("/about", methods=["GET", "POST"])
def game__about():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        bttn = request.form.get("bttn")

        if (page == "about"):

            if (bttn == "start"):

                ...

            elif (bttn == "new"):

                # Get new FIFTY_PACKAGE_GAME in Session
                session["fifty_package_game"] = game_fifty.get_fifty_package_game(db_pg,
                                                                                  session["user_id"])

                return redirect("/fifty/game")
            
            else:

                return redirect("/")
            
        else:

            return redirect("/")
    
    else:

        session.pop("fifty_package_game", None)
        session.pop("fifty_package_results", None)
        session.pop("fifty_package_review", None)
        
        return render_template("about.html", 
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

        page = request.form.get("page")
        goto = request.form.get("goto")
        bttn = request.form.get("bttn")

        if (page == "howto"):

            if (bttn == "start"):

                ...

            elif (bttn == "new"):

                # Get new FIFTY_PACKAGE_GAME in Session
                session["fifty_package_game"] = game_fifty.get_fifty_package_game(db_pg,
                                                                                  session["user_id"])

                return redirect("/fifty/game")
            
            else:

                return redirect("/")
            
        else:

            return redirect("/")
    
    else:
        
        session.pop("fifty_package_game", None)
        session.pop("fifty_package_results", None)
        session.pop("fifty_package_review", None)

        return render_template("howto.html", 
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
                        
                        session["login_msg"] = "Must provide username"
                        
                        return redirect("/login")

                    # Ensure password was submitted
                    elif not request.form.get("password"):

                        session["login_msg"] = "Must provide password"

                        return redirect("/login")

                    # Query database for username
                    user = get_user_info(db_pg, request.form.get("username"))

                    # Ensure username exists and password is correct
                    if user:

                        if not check_password_hash(user["hash"], request.form.get("password")):

                            session["login_msg"] = "Invalid username and/or password"

                            return redirect("/login")
                        
                    else:

                        session["login_msg"] = "Invalid username and/or password"

                        return redirect("/login")

                    # Remember which user has logged in
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    session["status"] = user["status"]
                    session["n1"] = 0 # game_geo.get_geo_kpi(db_pg, user["id"])
                    session["n2"] = game_fifty.get_fifty_kpi(db_pg, user["id"])

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

        try:
            login_msg = session["login_msg"]
        except:
            login_msg = " "

        session.pop("login_msg", None)

        return render_template("login.html", 
                               map_api_key=map_api_key,
                               new_registrations=new_registrations,
                               login_msg=login_msg)
    

####################################################################
# 
# ERROR
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
        
        return render_template("error.html",
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
# NAV 
#
####################################################################
@app.route("/nav", methods=["GET", "POST"])
def game__nav():

    if request.method == "POST":

        page = session["page"] = request.form.get("page")
        goto = session["goto"] = request.form.get("goto")
        nav = session["nav"] = request.form.get("nav")
        bttn = session["bttn"] = request.form.get("bttn")

        if session.get("user_id") is None:

            return redirect("/nav/out")
    
        else:

            return redirect("/nav/in")
    
    else:

        return apology("wrong page", 403)


####################################################################
# 
# NAV - OUT
#
####################################################################
@app.route("/nav/out", methods=["GET", "POST"])
def game__navout():

    if request.method == "POST":

        return apology("wrong page", 403)

    else:

        try:
            page = session["page"]
            goto = session["goto"]
            nav = session["nav"]
            bttn = session["bttn"]
        except:
            return apology("wrong page", 403)

        if (nav == "no"):

            return apology("wrong page", 403)
        
        elif (nav == "yes"):

            if (bttn == "about"):
                return redirect("/about")
            
            elif (bttn == "howto"):
                return redirect("/howto")
            
            elif (bttn == "index"):
                return redirect("/login")
            
            elif (bttn == "register"):
                return redirect("/register")
            
            elif (bttn == "login"):
                return redirect("/login")
            
            else:
                return apology("wrong page", 403)
    
        else:
            
            return apology("wrong page", 403)


####################################################################
# 
# NAV - IN
#
####################################################################
@app.route("/nav/in", methods=["GET", "POST"])
@login_required
def game__navin():

    if request.method == "POST":

        return apology("wrong page", 403)
    
    else:

        try:
            page = session["page"]
            goto = session["goto"]
            nav = session["nav"]
            bttn = session["bttn"]
        except:
            return apology("wrong page", 403)
        
        if (nav == "no"):

            return apology("wrong page", 403)
        
        elif (nav == "yes"):

            if (bttn == "about"):
                return redirect("/about")
            
            elif (bttn == "howto"):
                return redirect("/howto")
            
            elif (bttn == "index"):
                return redirect("/")
            
            # elif (bttn == "geo_page_dash"):
                
            #     try:
            #         session["geo_package_dash_today"]
            #         # session["geo_package_dash_header"]
            #         session["geo_package_dash_content"]
            #     except:
            #         session["geo_package_dash_today"] = datetime.now().strftime('%Y-%m-%d')
            #         # session["profile_package_geo"] = session["geo_package_dash_header"] = game_geo.get_geo_package_dash_header(db_pg, session["user_id"]) 
            #         session["geo_package_dash_content"] = game_geo.get_geo_package_dash_content(db_pg, session["user_id"])

            #     return redirect("/geo/dash")
            
            elif (bttn == "fifty_page_dash"):
                
                try:
                    session["fifty_package_dash_header"]
                    session["fifty_package_dash_content"]
                except:
                    session["profile_package_fifty"] = session["fifty_package_dash_header"] = game_fifty.get_fifty_package_dash_header(db_pg, session["user_id"]) 
                    session["fifty_package_dash_content"] = game_fifty.get_fifty_package_dash_content(db_pg, session["user_id"])
                
                return redirect("/fifty/dash")
            
            elif (bttn == "profile_page_main"):

                try:
                    session["profile_package_main"]
                    session["profile_package_geo"]
                    session["profile_package_fifty"]
                except:
                    session["profile_package_main"] = game_dash.get_dash_main(db_pg, session["user_id"])
                    # session["profile_package_geo"] = session["geo_package_dash_header"] = game_geo.get_geo_package_dash_header(db_pg, session["user_id"]) 
                    session["profile_package_fifty"] = session["fifty_package_dash_header"] = game_fifty.get_fifty_package_dash_header(db_pg, session["user_id"]) 

                return redirect("/profile")
            
            elif (bttn == "logout"):

                return redirect("/logout")

            else:

                return redirect("/")

        else:

            return apology("wrong page", 403)


# 1806 # 1627 # 1634 # 1682 # 1607 # 1571 # 1453 # 1394 # 1354 # 1349 # 1489