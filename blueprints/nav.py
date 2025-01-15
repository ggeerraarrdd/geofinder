# Python Standard Library
import os

# Third-Party Libraries
from flask import Blueprint, redirect, request, session

# Local Libraries
from helpers import apology, login_required
import game_fifty
import game_dash





# Create blueprint for core routes
nav = Blueprint('nav', __name__)

# Set constant variables
MAP_API_KEY = os.environ.get("MAP_API_KEY")
DATABASE_PG = os.environ.get("DATABASE_PG")


####################################################################
# 
# NAV 
#
####################################################################
@nav.route("/nav", methods=["GET", "POST"])
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
@nav.route("/nav/out", methods=["GET", "POST"])
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
@nav.route("/nav/in", methods=["GET", "POST"])
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
                    session["profile_package_fifty"] = session["fifty_package_dash_header"] = game_fifty.get_fifty_package_dash_header(DATABASE_PG, session["user_id"]) 
                    session["fifty_package_dash_content"] = game_fifty.get_fifty_package_dash_content(DATABASE_PG, session["user_id"])
                
                return redirect("/fifty/dash")
            
            elif (bttn == "profile_page_main"):

                try:
                    session["profile_package_main"]
                    session["profile_package_geo"]
                    session["profile_package_fifty"]
                except:
                    session["profile_package_main"] = game_dash.get_dash_main(DATABASE_PG, session["user_id"])
                    # session["profile_package_geo"] = session["geo_package_dash_header"] = game_geo.get_geo_package_dash_header(db_pg, session["user_id"]) 
                    session["profile_package_fifty"] = session["fifty_package_dash_header"] = game_fifty.get_fifty_package_dash_header(DATABASE_PG, session["user_id"]) 

                return redirect("/profile")
            
            elif (bttn == "logout"):

                return redirect("/logout")

            else:

                return redirect("/")

        else:

            return apology("wrong page", 403)
