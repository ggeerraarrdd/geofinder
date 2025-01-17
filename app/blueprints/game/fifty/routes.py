# Python Standard Library
import os

# Third-Party Libraries
from flask import redirect, render_template, request, session

# Local
import helpers
import crud
from . import fifty_bp





# Set constant variables
MAP_API_KEY = os.environ.get("MAP_API_KEY")
DATABASE_PG = os.environ.get("DATABASE_PG")


####################################################################
# 
# FIFTY - DASH
#
####################################################################
@fifty_bp.route("/fifty/dash", methods=["GET", "POST"])
@helpers.login_required
def game__fifty_dash():

    if request.method == "POST":

        page = request.form.get("page")
        goto = request.form.get("goto")
        nav = request.form.get("nav")
        bttn = request.form.get("bttn")

        if (page == "fifty_page_dash"):

            if (bttn == "review"):

                # Create new FIFTY_GAME_REVIEW package
                fifty_package_review = crud.get_fifty_package_review(DATABASE_PG, 
                                                                           session["user_id"], 
                                                                           request.form.get("loc"),
                                                                           request.form.get("time"),
                                                                           request.form.get("score"))

                # Save FIFTY_GAME_REVIEW package to Session
                session["fifty_package_review"] = fifty_package_review 

                return redirect("/fifty/review")
            
            elif (bttn == "start"):

                # Create FIFTY_PACKAGE_GAME package
                fifty_package_game = crud.get_fifty_package_game(DATABASE_PG, 
                                                                       session["user_id"])

                # Save FIFTY_PACKAGE_GAME package to Session
                session["fifty_package_game"] = fifty_package_game

                return redirect("/fifty/game")
            
            elif (bttn == "again"):

                # Create FIFTY_PACKAGE_GAME package
                fifty_package_game = crud.get_fifty_package_game_again(DATABASE_PG, 
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
                               map_api_key=MAP_API_KEY,
                               header=header,
                               content=content)


####################################################################
# 
# FIFTY - START
#
####################################################################
@fifty_bp.route("/fifty/start", methods=["GET", "POST"])
@helpers.login_required
def game__fifty_start():

    if request.method == "POST":

        return helpers.apology("wrong page", 403)

    else:

        if session.get("from_root"):

            session.pop("from_root")  

            # Create FIFTY_PACKAGE_GAME package
            fifty_package_game = crud.get_fifty_package_game(DATABASE_PG, 
                                                                session["user_id"])

            # Save FIFTY_PACKAGE_GAME package to Session
            session["fifty_package_game"] = fifty_package_game

            return redirect("/fifty/game")
    
        else:

            return helpers.apology("wrong page", 403)
    

####################################################################
# 
# FIFTY - GAME
#
####################################################################
@fifty_bp.route("/fifty/game", methods=["GET", "POST"])
@helpers.login_required
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
                    session["fifty_package_game"] = crud.get_fifty_package_game(DATABASE_PG, 
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
                fifty_package_results = crud.get_fifty_package_results(DATABASE_PG, 
                                                                             session["user_id"], 
                                                                             fifty_package_game,
                                                                             fifty_game_submit,
                                                                             fifty_game_submit_lat,
                                                                             fifty_game_submit_lng,
                                                                             fifty_game_submit_lat_display,
                                                                             fifty_game_submit_lng_display)

                # Update record
                crud.get_fifty_game_updated(DATABASE_PG, fifty_package_results)

                # Update n2
                session["n2"] = crud.get_fifty_kpi(DATABASE_PG, session["user_id"])

                # Update FIFTY_PACKAGE_DASH_HEADER and FIFTY_PACKAGE_DASH_CONTENT
                session["profile_package_fifty"] = session["fifty_package_dash_header"] = crud.get_fifty_package_dash_header(DATABASE_PG, session["user_id"]) 
                session["fifty_package_dash_content"] = crud.get_fifty_package_dash_content(DATABASE_PG, session["user_id"])

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
                                map_api_key=MAP_API_KEY,
                                package=package)
        
        else:

            return redirect("/fifty/dash")
        

####################################################################
#
# FIFTY - RESULTS
#
####################################################################
@fifty_bp.route("/fifty/results", methods=["GET", "POST"])
@helpers.login_required
def game__fifty_results():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "fifty_page_results"):

            if (bttn == "review"):

                # Create new FIFTY_GAME_REVIEW
                fifty_package_review = crud.get_fifty_package_review(DATABASE_PG, 
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

                    fifty_package_game = crud.get_fifty_package_game_again(DATABASE_PG, 
                                                                                 session["user_id"],
                                                                                 request.form.get("loc"))
                    
                    session["fifty_package_game"] = fifty_package_game
                
                    return redirect("/fifty/game")
                
                else:

                    return redirect("/fifty/dash")

            elif (bttn == "new"):

                # Get new FIFTY_PACKAGE_GAME in Session
                session["fifty_package_game"] = crud.get_fifty_package_game(DATABASE_PG,
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
                               map_api_key=MAP_API_KEY,
                               package=fifty_package_results)


####################################################################
# 
# FIFTY - REVIEW
#
####################################################################
@fifty_bp.route("/fifty/review", methods=["GET", "POST"])
@helpers.login_required
def game__fifty_review():

    if request.method == "POST":

        page = session["current_page"] = request.form.get("page")
        goto = session["current_goto"] = request.form.get("goto")
        bttn = session["current_bttn"] = request.form.get("bttn")

        if (page == "fifty_page_review"):
            
            if (bttn == "new"):

                    # Get new FIFTY_PACKAGE_GAME in Session
                    session["fifty_package_game"] = crud.get_fifty_package_game(DATABASE_PG, 
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
                               map_api_key=MAP_API_KEY,
                               package=fifty_package_review)
    
