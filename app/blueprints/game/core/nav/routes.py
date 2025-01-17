# Python Standard Library
import os

# Third-Party Libraries
from flask import redirect, request, session

# Local
import helpers 
import crud
from .. import nav_bp





# Set constant variables
MAP_API_KEY = os.environ.get("MAP_API_KEY")
DATABASE_PG = os.environ.get("DATABASE_PG")


####################################################################
# 
# NAV 
#
####################################################################
@nav_bp.route("/nav", methods=["GET", "POST"])
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

        return helpers.apology("wrong page", 403)


####################################################################
# 
# NAV - OUT
#
####################################################################
@nav_bp.route("/nav/out", methods=["GET", "POST"])
def game__navout():

    if request.method == "POST":

        return helpers.apology("wrong page", 403)

    else:

        try:
            page = session["page"]
            goto = session["goto"]
            nav = session["nav"]
            bttn = session["bttn"]
        except:
            return helpers.apology("wrong page", 403)

        if (nav == "no"):

            return helpers.apology("wrong page", 403)
        
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
                return helpers.apology("wrong page", 403)
    
        else:
            
            return helpers.apology("wrong page", 403)


####################################################################
# 
# NAV - IN
#
####################################################################
@nav_bp.route("/nav/in", methods=["GET", "POST"])
@helpers.login_required
def game__navin():

    if request.method == "POST":

        return helpers.apology("wrong page", 403)
    
    else:

        try:
            page = session["page"]
            goto = session["goto"]
            nav = session["nav"]
            bttn = session["bttn"]
        except:
            return helpers.apology("wrong page", 403)
        
        if (nav == "no"):

            return helpers.apology("wrong page", 403)
        
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
                    session["profile_package_fifty"] = session["fifty_package_dash_header"] = crud.get_fifty_package_dash_header(DATABASE_PG, session["user_id"]) 
                    session["fifty_package_dash_content"] = crud.get_fifty_package_dash_content(DATABASE_PG, session["user_id"])
                
                return redirect("/fifty/dash")
            
            elif (bttn == "profile_page_main"):

                session["from_root"] = True
                
                return redirect("/profile/start")
            
            elif (bttn == "logout"):

                return redirect("/logout")

            else:

                return redirect("/")

        else:

            return helpers.apology("wrong page", 403)
