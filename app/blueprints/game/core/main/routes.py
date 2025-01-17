# Python Standard Library
import os

# Third-Party Libraries
from flask import redirect, render_template, request, session

# Local
import helpers 
from .. import main_bp





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
# INDEX
#
####################################################################
@main_bp.route("/", methods=["GET", "POST"])
@helpers.login_required
def game__index():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        nav = request.form.get("nav")
        bttn = request.form.get("bttn")

        if (page == "index"):

            # Start bttn temp direct to Geo50x
            if (bttn == "temp"):

                session["from_root"] = True

                return redirect("/fifty/start")

            else:

                return helpers.apology("wrong page", 403)

        else:

            return helpers.apology("wrong page", 403)
        
    else:

        return render_template("index.html", 
                               map_api_key=MAP_API_KEY,
                               new_registrations=new_registrations)
    

####################################################################
# 
# ABOUT
#
####################################################################
@main_bp.route("/about", methods=["GET", "POST"])
def game__about():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        bttn = request.form.get("bttn")

        if (page == "about"):

            if (bttn == "start"):

                ...

            elif (bttn == "new"):

                session["from_root"] = True

                return redirect("/fifty/start")
            
            else:

                return redirect("/")
            
        else:

            return redirect("/")
    
    else:

        session.pop("fifty_package_game", None)
        session.pop("fifty_package_results", None)
        session.pop("fifty_package_review", None)
        
        return render_template("about.html", 
                            map_api_key=MAP_API_KEY,
                            new_registrations=new_registrations)


####################################################################
# 
# HOW TO PLAY
#
####################################################################
@main_bp.route("/howto", methods=["GET", "POST"])
def game__howto():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        bttn = request.form.get("bttn")

        if (page == "howto"):

            if (bttn == "start"):

                ...

            elif (bttn == "new"):

                session["from_root"] = True

                return redirect("/fifty/start")
            
            else:

                return redirect("/")
            
        else:

            return redirect("/")
    
    else:
        
        session.pop("fifty_package_game", None)
        session.pop("fifty_package_results", None)
        session.pop("fifty_package_review", None)

        return render_template("howto.html", 
                               map_api_key=MAP_API_KEY,
                               new_registrations=new_registrations)


####################################################################
# 
# ERROR
#
####################################################################
@main_bp.route("/error", methods=["GET", "POST"])
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
                               map_api_key=MAP_API_KEY,
                               new_registrations=new_registrations,
                               error=error)
    
