# Python Standard Library
import os

# Third-Party Libraries
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

# Local 
import helpers
import crud 
from .. import authy_bp





# Set constant variables
MAP_API_KEY = os.environ.get("MAP_API_KEY")
DATABASE_PG = os.environ.get("DATABASE_PG")

# Set registration status
try:
    new_registrations = False if os.environ.get("NEW_REGISTRATIONS").upper() == "FALSE" else True
except:
    new_registrations = False


####################################################################
# 
# REGISTER 
#
####################################################################
@authy_bp.route("/register", methods=["GET", "POST"])
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

                    return helpers.apology("must provide username", 400)
                
                # Ensure password was submitted
                elif not request.form.get("password"):

                    return helpers.apology("must provide password", 400)
                
                else:

                    # Ensure password and confirmation match
                    new_password = request.form.get("password")
                    confirmation = request.form.get("confirmation")

                    if new_password == confirmation:

                        new_username = request.form.get("username")
                        new_password = generate_password_hash(confirmation)

                        results = crud.get_registered(DATABASE_PG, new_username, new_password)

                        if results != 1:
                            return helpers.apology("username is already taken", 400)
                        else:
                            return redirect("/")
                    
                    else:

                        return helpers.apology("password did not match", 400)
            
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
                                   map_api_key=MAP_API_KEY,
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
@authy_bp.route("/login", methods=["GET", "POST"])
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
                    user = crud.get_user_info(DATABASE_PG, request.form.get("username"))

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
                    session["n2"] = crud.get_fifty_kpi(DATABASE_PG, user["id"])

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
                               map_api_key=MAP_API_KEY,
                               new_registrations=new_registrations,
                               login_msg=login_msg)
        

####################################################################
# 
# LOGOUT 
#
####################################################################
@authy_bp.route("/logout", methods=["GET", "POST"])
def game__logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
