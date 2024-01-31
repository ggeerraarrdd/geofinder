import psycopg2
from psycopg2.extras import RealDictCursor
from random import randint
from datetime import datetime, timezone
import pytz
from math import ceil, exp
from helpers import latitude_offset, longitude_offset


def get_fifty_playable_location(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM locations 
        WHERE loc_game = 'geo50x' 
        AND id NOT IN 
            (
            SELECT DISTINCT fifty_game_loc_id 
            FROM games_fifty
            WHERE fifty_game_user_id = %s
            AND (fifty_game_submit_validation > 0 OR  fifty_game_submit_validation > 0)
            ) 
        AND loc_playable = TRUE 
        ; 
        """

    # Run query
    cursor.execute(query, (user_id,))

    # Get playable locations
    locs_playable = cursor.fetchall()
    
    # Get count of playable locations
    locs_playable_count = len(locs_playable)

    # Get results
    if locs_playable_count == 0:
        results = None
    else: 
        # Generate random number in range to loc_playable
        row = randint(0, locs_playable_count - 1)

        # Get row
        results = locs_playable[row]

    cursor.close()
    conn.close()

    return results 


def get_fifty_playable_location_again(db, current_game_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM locations 
        WHERE id = %s 
        AND loc_game = 'geo50x'; 
        """
    
    # Run query
    cursor.execute(query, (current_game_id,))
    
    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


def get_fifty_game_started(db, user_id, loc_id):

    # Set game start time
    # TODO Change to datetime.now(timezone.utc) for all use
    now = datetime.now(timezone.utc).astimezone(pytz.timezone('US/Central'))

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        INSERT INTO games_fifty (fifty_game_user_id, fifty_game_loc_id, fifty_game_start, fifty_game_end) 
        VALUES (%s, %s, %s, %s) 
        RETURNING fifty_game_id;
        """

    # Run query
    cursor.execute(query, (user_id, loc_id, now, now))

    # Get results
    results = cursor.fetchone()

    # Commit insert
    conn.commit()

    cursor.close()
    conn.close()

    return(results["fifty_game_id"], now)


def get_fifty_game_score(db, user_id, location_id, validation, duration):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT count(*) AS count 
        FROM games_fifty 
        WHERE fifty_game_user_id = %s 
        AND fifty_game_loc_id = %s; 
        """

    # Run query
    cursor.execute(query, (user_id, location_id))

    # Get pre-results
    pre_results = cursor.fetchone()

    # Get attempts from pre-results
    attempts = int(pre_results["count"])

    # TODO Calculate total duration of all attempts
    
    # Calculate score
    if validation == 1:
        
        # Calculate base
        if attempts <= 1:
            base = 50
        elif attempts == 2:
            base = 40
        else:
            base = 30

        # Calculate bonus
        bonus_multiplier = exp(-0.0054*(ceil(duration/60)-1)**2)
        bonus = round(50 * bonus_multiplier)
    
    else:
        base = 0
        bonus = 0

    # Get results
    results = {
        "attempts" : attempts,
        "base": base,
        "bonus": bonus,
        "total": base + bonus
    }

    cursor.close()
    conn.close()

    return results


def get_fifty_game_updated(db, package):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query 
    query = """
        UPDATE games_fifty SET 
            fifty_game_end = %s, 
            fifty_game_submit = %s, 
            fifty_game_submit_coor = ST_SetSRID(ST_MakePoint(%s, %s), 4326), 
            fifty_game_submit_lat = %s, 
            fifty_game_submit_lng = %s, 
            fifty_game_submit_off = %s, 
            fifty_game_submit_validation = %s,
            fifty_game_duration = %s, 
            fifty_game_score_base = %s,
            fifty_game_score_bonus = %s  
        WHERE fifty_game_id = %s; 
        """

    # Run query
    cursor.execute(query, (package["fifty_game_end"], 
                           package["fifty_game_submit"], 
                           package["fifty_game_submit_lng"], 
                           package["fifty_game_submit_lat"], 
                           package["fifty_game_submit_lat"], 
                           package["fifty_game_submit_lng"], 
                           package["fifty_game_submit_off"], 
                           package["fifty_game_submit_validation"], 
                           package["fifty_game_duration_display"], 
                           package["fifty_game_score_base_display"], 
                           package["fifty_game_score_bonus_display"], 
                           package["fifty_game_id"]))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1


def get_fifty_game_deleted(db, game_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Set query
    query = "DELETE FROM games_fifty WHERE fifty_game_id = %s; "
    
    # Run query
    cursor.execute(query, (game_id,))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1


def get_fifty_game_reviewed(db, user_id, loc_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get location info
    query = "SELECT * FROM locations WHERE id = %s; "
    cursor.execute(query, (loc_id,))
    loc_info = cursor.fetchone()

    # Get game info - attempted w/ answer (right)
    query = """
        SELECT fifty_game_submit_lat, fifty_game_submit_lng 
        FROM games_fifty
        WHERE fifty_game_user_id = %s 
        AND fifty_game_loc_id = %s 
        AND fifty_game_submit_lat IS NOT NULL 
        AND fifty_game_submit_lng IS NOT NULL 
        AND fifty_game_submit_validation = 1; 
        """
    cursor.execute(query, (user_id, loc_id))
    locations_right = cursor.fetchone()

    try:
        locations_right = [{key: value for key, value in locations_right.items()}]
    except AttributeError:
        locations_right = []
    
    # Get game info - attempted w/ answer (wrong)
    query = """
        SELECT fifty_game_submit_lat, fifty_game_submit_lng 
        FROM games_fifty 
        WHERE fifty_game_user_id = %s 
        AND fifty_game_loc_id = %s 
        AND fifty_game_submit_lat IS NOT NULL 
        AND fifty_game_submit_lng IS NOT NULL 
        AND fifty_game_submit_validation = 0; 
        """
    cursor.execute(query, (user_id, loc_id))
    locations_wrong = cursor.fetchall()
    # locations_wrong = [{key: value for key, value in row.items()} for row in locations_wrong]

    try:
        locations_wrong = [{key: value for key, value in row.items()} for row in locations_wrong]
    except AttributeError:
        locations_wrong = []

    # Get games info - attempted w/ answer (none)
    query = """
        SELECT count(*) 
        FROM games_fifty 
        WHERE fifty_game_user_id = %s 
        AND fifty_game_loc_id = %s 
        AND fifty_game_submit = 0 
        AND fifty_game_submit_validation = 0; 
        """
    cursor.execute(query, (user_id, loc_id))
    locations_none = cursor.fetchone()

    # Get games info - attempted w/ answer (none) - quit
    query = """
        SELECT 
            COALESCE(gf.fifty_game_submit_lat, l.loc_key_lat) AS game_lat, 
            COALESCE(gf.fifty_game_submit_lng, l.loc_key_lng) AS game_lng 
        FROM games_fifty AS gf 
        JOIN locations AS l ON gf.fifty_game_loc_id = l.id 
        WHERE gf.fifty_game_user_id = %s 
        AND l.id = %s 
        AND gf.fifty_game_submit_validation = 2; 
        """
    cursor.execute(query, (user_id, loc_id))
    locations_quit = cursor.fetchall()
    
    try:
        locations_quit = [{key: value for key, value in row.items()} for row in locations_quit]
    except AttributeError:
        locations_quit = []

    # Get total duration
    query = """
        WITH cte AS 
            ( 
            SELECT sum(EXTRACT(EPOCH FROM (fifty_game_end - fifty_game_start))) AS seconds 
            FROM games_fifty 
            WHERE fifty_game_user_id = %s AND fifty_game_loc_id = %s 
            ) 
        SELECT to_char(INTERVAL '1 second' * seconds, 'HH24:MI:SS') AS time_clock 
        FROM cte; 
        """
    cursor.execute(query, (user_id, loc_id))
    time_clock = cursor.fetchone()

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

    get_fifty_game_review = {
        "game_id": loc_info["id"],
        "loc_view_lat": loc_info["loc_view_lat"],
        "loc_view_lng": loc_info["loc_view_lng"],
        "loc_lat_offsets": loc_lat_game_offset,
        "locations_right": locations_right,
        "locations_wrong": locations_wrong,
        "locations_none": locations_shift,
        "locations_quit": locations_quit,
        "loc_city": loc_info["loc_city"],
        "loc_state": loc_info["loc_state"],
        "loc_country": loc_info["loc_country"],
        "loc_image_source": loc_info["loc_image_source"],
        "loc_url_source": loc_info["loc_url_source"],
        "time_clock": time_clock["time_clock"],
    }

    # Close cursor and connection
    cursor.close()
    conn.close()

    return get_fifty_game_review

