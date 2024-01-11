import psycopg2
from psycopg2.extras import RealDictCursor
from random import randint
from datetime import datetime
from math import floor, ceil, exp, radians, degrees, cos, sqrt
from haversine import haversine, Unit
import time
import requests


def get_registered(db, new_username, new_password):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Create query
    query = "INSERT INTO users (username, hash) "
    query = query + "VALUES (%s, %s); "

    # Execute query
    cursor.execute(query, (new_username, new_password))

    # Commit insert
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_user_info(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Create query
    query = "SELECT * "
    query = query + "FROM users "
    query = query + "WHERE username = %s; "

    cursor.execute(query, (user_id,))
    user_info = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return(user_info)


def get_total_score(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT sum(game_score) AS total "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s; "

    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    try:
        total = int(result["total"])
    except TypeError:
        total = 0

    # Close cursor and connection
    cursor.close()
    conn.close()

    return total


def get_summary_percent(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations count
    query = "SELECT "
    query = query + "COALESCE(ROUND(SUM(game_score)::NUMERIC / COUNT(*), 1), 0) AS user_summary_percent "
    query = query + "FROM games "
    query = query + "WHERE game_answer_validation > 0 "
    query = query + "AND user_id = %s; "
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()

    try:
        results = int(results["user_summary_percent"])
    except TypeError:
        results = 0

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_playable_location(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations
    query = "SELECT * "
    query = query + "FROM locs "
    query = query + "WHERE id NOT IN "
    query = query + "( "
    query = query + "SELECT DISTINCT loc_id "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s "
    query = query + "AND game_answer_validation > 0 "
    query = query + ") "
    query = query + "AND loc_playable = TRUE; "
    cursor.execute(query, (user_id,))
    locs_playable = cursor.fetchall()
    
    # Get count of playable locations
    locs_playable_count = len(locs_playable)

    if locs_playable_count == 0:
        location = None
    else: 
        # Generate random number in range to loc_playable
        row = randint(0, locs_playable_count - 1)

        # Get row
        location = dict(locs_playable[row])

    cursor.close()
    conn.close()

    return location 


def get_playable_location_again(db, current_game_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations
    query = "SELECT * "
    query = query + "FROM locs "
    query = query + "WHERE id = %s; "
    cursor.execute(query, (current_game_id,))
    locs_playable = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return locs_playable


def start_game(db, user_id, loc_id):

    # Set game start time
    # TODO All times default to CST
    now = datetime.now()

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = "INSERT INTO games (user_id, loc_id, game_start, game_end) VALUES "
    query = query + "(%s, %s, %s, %s) "
    query = query + "RETURNING id; "
    cursor.execute(query, (user_id, loc_id, now, now))

    game_new = cursor.fetchone()

    # Commit insert
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return(game_new["id"], now)


def get_game_info(db, id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = "SELECT * FROM games WHERE id = %s; "
    cursor.execute(query, (id,))
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return(results)


def get_locs_info(db, id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = "SELECT * FROM locs WHERE id = %s; "
    cursor.execute(query, (id,))
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return(results)


def update_current_game(db, updates):

    # TODO try-catch db connection
    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Update game record on games table
    query = "UPDATE games SET "
    query = query + "game_end = %s, "
    query = query + "game_submit_coor = ST_SetSRID(ST_MakePoint(%s, %s), 4326), "
    query = query + "game_submit_lat = %s, " 
    query = query + "game_submit_lng = %s, " 
    query = query + "game_user_quit = %s, " 
    query = query + "game_answer_off = %s, "
    query = query + "game_answer_validation = %s, " 
    query = query + "game_duration = %s, "
    query = query + "game_score = %s "
    query = query + "WHERE id = %s; "
    cursor.execute(query, (updates["game_end"], 
                           updates["game_lng"], 
                           updates["game_lat"], 
                           updates["game_lat"], 
                           updates["game_lng"], 
                           updates["game_user_quit"], 
                           updates["game_answer_off"], 
                           updates["game_answer_validation"], 
                           updates["game_duration"], 
                           updates["game_score"], 
                           updates["id"]))

    # Commit update
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_current_game_deleted(db, current_game_id):

    # TODO try-catch db connection
    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Delete game record on games table
    query = "DELETE FROM games WHERE id = %s; "
    cursor.execute(query, (current_game_id,))

    # Commit update
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_disconnected(db, current_game_id, current_game_start):

    # Set current timestamp
    current_game_end = datetime.now()
    
    # Delay function by 5 seconds to allow other functions to update db
    time.sleep(5)

    # TODO try-catch db connection
    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Check value of game_duration
    query = "SELECT game_duration FROM games WHERE id = %s; "
    cursor.execute(query, (current_game_id,))
    result = cursor.fetchone()

    # Check if game record is deleted or still there
    if result == None: 
        # Game record has been deleted
        result = f"Game record has been deleted."
    
    else:
        # Game record is still there & game_duration is still None
        if result[0] == None:
            # Calculate duration
            duration_sec, duration_min = game_answer_duration(current_game_start, current_game_end)

            if duration_sec >= 10:
                # Update game_duration
                query = "UPDATE games SET game_duration = %s WHERE id = %s; "
                cursor.execute(query, (duration_min, current_game_id))

                # Commit update
                conn.commit()

                result = f"Game record updated."
            
            else:
                get_current_game_deleted(db, current_game_id)
                result = f"Game record deleted."
        
        # Game record is still there & game_duration is still None
        else:
            result = f"Game record has game_duration."
    
    # Close cursor and connection
    cursor.close()
    conn.close()

    return result


def game_answer_distance(loc_key_lat, loc_key_long, game_submit_lat, game_submit_long):

    # https://pypi.org/project/haversine/
    # https://en.wikipedia.org/wiki/Haversine_formula
    # Calculate distance between answer coordinates and user-submitted coordinates
    # Distance in feet

    answer = (float(loc_key_lat), float(loc_key_long))
    submitted = (float(game_submit_lat), float(game_submit_long))

    game_answer_distance = haversine(answer, submitted, unit=Unit.FEET)
    game_answer_distance = floor(game_answer_distance)

    return game_answer_distance


def game_answer_duration(game_start, game_end):

    # Calculate time difference in seconds
    game_duration = game_end - game_start
    duration_sec = game_duration.seconds
    duration_min = ceil(game_duration.seconds / 60)

    return duration_sec, duration_min


def get_loc_duration_total(db, current_game_id, user_id, loc_id, current_game_duration):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT COALESCE(SUM(game_duration), 0) AS total "
    query = query + "FROM games "
    query = query + "WHERE id != %s "
    query = query + "AND user_id = %s "
    query = query + "AND loc_id = %s; "
    cursor.execute(query, (current_game_id, user_id, loc_id))
    result = cursor.fetchone()
                        
    total = int(result["total"]) + int(current_game_duration)

    # Close cursor and connection
    cursor.close()
    conn.close()

    return total


def game_answer_score(db, user_id, location_id, validation, duration):

    base_score = 0
    bonus_score = 0
    bonus_score_multiplier = 0

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Calculate max base score based on attempts
    query = "SELECT count(*) AS count "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s "
    query = query + "AND loc_id = %s; "
    cursor.execute(query, (user_id, location_id))
    result = cursor.fetchone()
    attempts = int(result["count"])

    if attempts <= 1:
        base_score_add = 50
    elif attempts == 2:
        base_score_add = 40
    else:
        base_score_add = 30

    # TODO Calculate total duration of all attempts
    
    # Calculate actual score based on validation and duration
    if validation == 1:
        base_score = base_score + base_score_add
        bonus_score_multiplier = exp(-0.0054*(ceil(duration/60)-1)**2)
        bonus_score = round(50 * bonus_score_multiplier)

    # Calculate game score
    game_score = base_score + bonus_score

    # Close cursor and connection
    cursor.close()
    conn.close()

    return base_score, bonus_score, game_score, attempts


def get_history(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations count
    query = "SELECT * "
    query = query + "FROM locs "
    query = query + "WHERE id NOT IN (SELECT DISTINCT loc_id FROM games WHERE user_id = %s AND game_answer_validation > 0) "
    query = query + "AND loc_playable = TRUE; "
    cursor.execute(query, (user_id,))
    locs_playable = cursor.fetchall()
    locs_playable_count = len(locs_playable)

    # Get history
    query = "WITH cte AS "
    query = query + "( "
    query = query + "SELECT "
    query = query + "DISTINCT loc_id "
    query = query + ",CASE WHEN sum(game_answer_validation) OVER (PARTITION BY loc_id) > 1 THEN 'N' WHEN game_score = 0 THEN '-' ELSE 'Y' END AS found "
    query = query + ",sum(game_answer_validation) OVER (PARTITION BY loc_id) AS total_game_answer_validation "
    query = query + ",count(*) OVER (PARTITION BY loc_id) AS total_attempts "
    query = query + ",sum(game_duration) OVER (PARTITION BY loc_id) AS total_duration "
    query = query + ",sum(game_duration) OVER (PARTITION BY loc_id) / count(*) OVER (PARTITION BY loc_id) AS avg_time "
    query = query + ",sum(game_answer_off) OVER (PARTITION BY loc_id) / count(*) OVER (PARTITION BY loc_id) AS avg_offset "
    query = query + ",sum(game_score) OVER (PARTITION BY loc_id) AS score  "
    query = query + ",loc_city "
    query = query + ",loc_state "
    query = query + ",loc_country "
    query = query + "FROM games "
    query = query + "JOIN locs ON games.loc_id = locs.id "
    query = query + "WHERE user_id = %s "
    query = query + "ORDER BY loc_id "
    query = query + ") "
    query = query + "SELECT * FROM cte WHERE NOT (found = '-' AND score > 0); "
    cursor.execute(query, (user_id,))
    history = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return locs_playable_count, history


def get_profile_user(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations count
    query = "SELECT * FROM users WHERE id = %s; "
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_profile_summary(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations count
    query = "SELECT "
    query = query + "COALESCE(SUM(CASE WHEN game_answer_validation > 0 THEN 1 ELSE 0 END), 0) AS user_count_loc, "
    query = query + "COALESCE(SUM(CASE WHEN game_answer_validation > 0 THEN game_score ELSE 0 END), 0) AS user_score_total, "
    query = query + "COALESCE(SUM(CASE WHEN game_answer_validation > 0 THEN 1 ELSE 0 END) * 100, 0) AS user_score_possible, "
    query = query + "COALESCE(ROUND(SUM(CASE WHEN game_answer_validation > 0 THEN game_score ELSE 0 END) / SUM(CASE WHEN game_answer_validation > 0 THEN 1 ELSE 0 END), 1), 0) AS user_score_percentage, "
    query = query + "COALESCE(SUM(game_duration), 0) AS user_duration_total, "
    query = query + "COALESCE(AVG(game_duration), 0) AS user_duration_average, "
    query = query + "COALESCE(ROUND(SUM(game_answer_off)::NUMERIC / count(*)), 0) AS user_offset_avg, "
    query = query + "TO_CHAR(MAX(game_end), 'YYYY-MM-DD') AS last_game, "
    query = query + "EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(game_end))) AS days "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s; "
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_profile_updated_username(db, username, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Update game record on games table
    query = "UPDATE users SET "
    query = query + "username = %s, "
    query = query + "date_updated = CURRENT_TIMESTAMP "
    query = query + "WHERE id = %s; "
    cursor.execute(query, (username, id))

    # Commit update
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_profile_updated_country(db, country, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Update game record on games table
    query = "UPDATE users SET "
    query = query + "country = %s, "
    query = query + "date_updated = CURRENT_TIMESTAMP "
    query = query + "WHERE id = %s; "
    cursor.execute(query, (country, id))

    # Commit update
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_profile_updated_password(db, password, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Update game record on games table
    query = "UPDATE users SET "
    query = query + "hash = %s, "
    query = query + "date_updated = CURRENT_TIMESTAMP "
    query = query + "WHERE id = %s; "
    cursor.execute(query, (password, id))

    # Commit update
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_history_review(db, user_id, loc_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get location info
    query = "SELECT * FROM locs WHERE id = %s; "
    cursor.execute(query, (loc_id,))
    loc_info = cursor.fetchone()

    # Get games info - attempted w/ answer (right)
    query = "SELECT game_submit_lat, game_submit_lng "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s "
    query = query + "AND loc_id = %s "
    query = query + "AND game_submit_lat IS NOT NULL "
    query = query + "AND game_submit_lng IS NOT NULL "
    query = query + "AND game_answer_validation = 1; "
    cursor.execute(query, (user_id, loc_id))
    locations_right = cursor.fetchone()

    try:
        locations_right = [{key: value for key, value in locations_right.items()}]
    except AttributeError:
        locations_right = []
    
    # Get games info - attempted w/ answer (wrong)
    query = "SELECT game_submit_lat, game_submit_lng "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s "
    query = query + "AND loc_id = %s "
    query = query + "AND game_submit_lat IS NOT NULL "
    query = query + "AND game_submit_lng IS NOT NULL "
    query = query + "AND game_answer_validation = 0; "
    cursor.execute(query, (user_id, loc_id))
    locations_wrong = cursor.fetchall()
    locations_wrong = [{key: value for key, value in row.items()} for row in locations_wrong]

    try:
        locations_wrong = [{key: value for key, value in row.items()} for row in locations_wrong]
    except AttributeError:
        locations_wrong = []

    # Get games info - attempted w/ answer (none)
    query = "SELECT count(*) "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s "
    query = query + "AND loc_id = %s "
    query = query + "AND game_user_quit = 1 "
    query = query + "AND game_answer_validation = 0; "
    cursor.execute(query, (user_id, loc_id))
    locations_none = cursor.fetchone()

    # Get games info - attempted w/ answer (none) - quit
    query = "SELECT "
    query = query + "COALESCE(g.game_submit_lat, l.loc_key_lat) AS game_lat, "
    query = query + "COALESCE(g.game_submit_lng, l.loc_key_lng) AS game_lng "
    query = query + "FROM games AS g "
    query = query + "JOIN locs AS l ON g.loc_id = l.id "
    query = query + "WHERE user_id = %s "
    query = query + "AND l.id = %s "
    query = query + "AND g.game_answer_validation = 2; "
    cursor.execute(query, (user_id, loc_id))
    locations_quit = cursor.fetchall()
    
    try:
        locations_quit = [{key: value for key, value in row.items()} for row in locations_quit]
    except AttributeError:
        locations_quit = []

    # Get total duration
    query = "WITH cte AS "
    query = query + "( "
    query = query + "SELECT sum(EXTRACT(EPOCH FROM (game_end - game_start))) AS seconds "
    query = query + "FROM games "
    query = query + "WHERE user_id = %s AND loc_id = %s "
    query = query + ") "
    query = query + "SELECT to_char(INTERVAL '1 second' * seconds, 'HH24:MI:SS') AS time_clock "
    query = query + "FROM cte; "
    cursor.execute(query, (user_id, loc_id))
    time_clock = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return loc_info, locations_right, locations_wrong, locations_none, locations_quit, time_clock


def get_locs(db):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations count
    query = "SELECT * FROM locs ORDER BY id; "
    cursor.execute(query)
    locs = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return locs


def get_locs_single(db, id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = "SELECT * FROM locs WHERE id = %s; "
    cursor.execute(query, (id,))
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return(results)


def get_locs_corners(latitude, longitude):
    R = 6371.0  # Radius of the Earth in kilometers

    # Convert latitude and longitude to radians
    lat_rad = radians(latitude)
    lon_rad = radians(longitude)

    # Calculate the distance (in kilometers) to each corner of the box
    diagonal_distance = 0.01 * sqrt(2)
    half_diagonal_distance = diagonal_distance / 2
    north_distance = half_diagonal_distance / R
    east_distance = half_diagonal_distance / (R * cos(lat_rad))

    # Calculate the coordinates of the corners
    north_lat = latitude + degrees(north_distance)
    south_lat = latitude - degrees(north_distance)
    east_lon = longitude + degrees(east_distance)
    west_lon = longitude - degrees(east_distance)

    polygon = [
        {
            # northwest
            "lat": north_lat,
            "lng": west_lon
        },
        {
            # northeast
            "lat": north_lat,
            "lng": east_lon
        },
        {
            # southeast
            "lat": south_lat,
            "lng": east_lon
        },
        {
            # southwest
            "lat": south_lat,
            "lng": west_lon
        }
    ]

    return polygon


def get_locs_refreshed(db):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = "SELECT * FROM locs ORDER BY id; "
    cursor.execute(query)
    rows = cursor.fetchall()

    # Validate loc_url_source
    print("VALIDATE URLS")
    for row in rows:
        id, url = row["id"], row["loc_url_source"]
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"{id} is accessible.")
            else:
                # Update is_active if URL is not accessible
                update_query = f"UPDATE locs SET is_active = FALSE WHERE id = {id}; "
                cursor.execute(update_query)
                print(f"{id} is not accessible. The is_active column has been updated.")
        except requests.exceptions.RequestException:
            # Update the column in that row to indicate the URL is not accessible
            update_query = f"UPDATE locs SET is_active = FALSE WHERE id = {id}; "
            cursor.execute(update_query)
            print(f"{id} is not accessible. The is_active column has been updated.")
    
    # Validate is_playable
    print("VALIDATE IMAGES")
    for row in rows:
        id, url = row["id"], row["loc_image_source"]
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"{id} is accessible.")
            else:
                # Update is_active if URL is not accessible
                update_query = f"UPDATE locs SET loc_image_valid = FALSE WHERE id = {id}; "
                cursor.execute(update_query)
                print(f"{id} is not accessible. The loc_image_valid column has been updated.")
        except requests.exceptions.RequestException:
            # Update the column in that row to indicate the URL is not accessible
            update_query = f"UPDATE locs SET loc_image_valid = FALSE WHERE id = {id}; "
            cursor.execute(update_query)
            print(f"{id} is not accessible. The accessibility column has been updated.")

    # Validate locations
    print("VALIDATE LOCATIONS")
    for row in rows:
        id = row["id"]
        playable = row["loc_playable"]
        removed = row["loc_removed"]
        url = row["loc_url_valid"]
        image = row["loc_image_valid"]
        key = row["loc_key_shp_valid"]

        if (not removed) and (url) and (image) and (key):
            if not playable:
                update_query = f"UPDATE locs SET loc_playable = TRUE WHERE id = {id}; "
                cursor.execute(update_query)
                print(f"{id} is playable. The loc_playable column has been updated")
            else:
                print(f"{id} is playable.")
        else:
            if playable:
                update_query = f"UPDATE locs SET loc_playable = FALSE WHERE id = {id}; "
                cursor.execute(update_query)
                print(f"{id} is not playable. The loc_playable column has been updated")
            else:
                print(f"{id} is not playable.")

    # Commit the changes
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_locs_fifty_status(db):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = "SELECT "
    query = query + "SUM(CASE WHEN loc_playable = FALSE THEN 1 ELSE 0 END) AS loc_playable, "
    query = query + "SUM(CASE WHEN loc_url_valid = FALSE THEN 1 ELSE 0 END) AS loc_url_valid, "
    query = query + "SUM(CASE WHEN loc_image_valid = FALSE THEN 1 ELSE 0 END) AS loc_image_valid, "
    query = query + "SUM(CASE WHEN loc_key_shp_valid = FALSE THEN 1 ELSE 0 END) AS loc_key_shp_valid "
    query = query + "FROM locs; "

    cursor.execute(query, (id,))
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return(results)


def get_table_admin_users(db):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations count
    query = "SELECT "
    query = query + "u.id, "
    query = query + "u.status, "
    query = query + "u.username, "
    query = query + "u.country, "
    query = query + "u.icon, "
    query = query + "TO_CHAR(u.date_add, 'YYYY-MM-DD') date_add, "
    query = query + "EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(g.game_end))) AS last_game_date "
    query = query + "FROM games AS g "
    query = query + "RIGHT JOIN users AS u ON g.user_id = u.id "
    query = query + "GROUP BY u.id "
    query = query + "ORDER BY u.id; "
    cursor.execute(query)
    results = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_header_admin_users(db):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get playable locations count
    query = "WITH cte AS "
    query = query + "( "
    query = query + "SELECT u.id, u.username, u.date_add, MAX(g.game_end) AS last_game_date "
    query = query + "FROM games AS g "
    query = query + "RIGHT JOIN users AS u ON g.user_id = u.id "
    query = query + "GROUP BY u.id "
    query = query + ") "
    query = query + "SELECT  "
    query = query + "COUNT(*) AS user_count, "
    query = query + "SUM(CASE WHEN EXTRACT(DAY FROM AGE(CURRENT_DATE, last_game_date)) < 8 THEN 1 ELSE 0 END) AS user_active, "
    query = query + "EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(date_add))) AS last_user_registration, "
    query = query + "EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(last_game_date))) AS last_user_game "
    query = query + "FROM cte; "
    cursor.execute(query)
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results

