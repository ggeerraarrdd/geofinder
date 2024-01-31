import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from helpers import latitude_offset, longitude_offset


def get_geo_today_location_info(db):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = """
        SELECT * 
        FROM geofinder AS g 
        JOIN locations AS l ON g.geofinder_locations_id = l.id 
        WHERE g.geofinder_date = (CURRENT_TIMESTAMP AT TIME ZONE 'US/Central')::date;
        """

    cursor.execute(query)
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_geo_today_location_status(db, user_id, geofinder_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT COALESCE((SELECT geo_game_id 
        FROM games_geofinder 
        WHERE geo_game_user_id = %s
        AND geo_game_geofinder_id = %s 
        AND geo_game_submit_validation > 0), 0) AS geo_game_id;
        """

    # Run query
    cursor.execute(query, (user_id, geofinder_id,))

    # Get results
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return(results)


def get_geo_game_created(db, user_id, geofinder_id):

    # Set game start time
    # TODO All times default to CST
    now = datetime.now()

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = "INSERT INTO games_geofinder (geo_game_user_id, geo_game_geofinder_id, geo_game_start) VALUES "
    query = query + "(%s, %s, %s) "
    query = query + "RETURNING geo_game_id; "

    # Run query
    cursor.execute(query, (user_id, geofinder_id, now,))

    # Get results
    results = cursor.fetchone()

    # Commit insert
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results["geo_game_id"] 


def get_geo_game_started(db, geo_game_id):

    # Set game start time
    # TODO All times default to CST
    now = datetime.now()

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            gg.geo_game_id,
            gg.geo_game_start,
            g.*,
            l.*
        FROM games_geofinder AS gg
        JOIN geofinder AS g ON gg.geo_game_geofinder_id = g.geofinder_id
        JOIN locations AS l ON g.geofinder_locations_id = l.id 
        WHERE geo_game_id = %s; 
        """

    # Run query
    cursor.execute(query, (geo_game_id,))

    # Get query results
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_geo_game_updated(db, updates):

    # TODO try-catch db connection
    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = "UPDATE games_geofinder SET "
    query = query + "geo_game_end = %s, "
    query = query + "geo_game_submit = %s, "
    query = query + "geo_game_submit_lat = %s, " 
    query = query + "geo_game_submit_lng = %s, " 
    query = query + "geo_game_submit_off = %s, "
    query = query + "geo_game_submit_validation = %s, " 
    query = query + "geo_game_duration = %s, "
    query = query + "geo_game_score_base = %s, "
    query = query + "geo_game_score_bonus = %s "
    query = query + "WHERE geo_game_id = %s; "

    # Run query
    cursor.execute(query, (updates["geo_game_end"], 
                           updates["geo_game_submit"],
                           updates["geo_game_submit_lat"], 
                           updates["geo_game_submit_lng"], 
                           updates["geo_game_submit_off"], 
                           updates["geo_game_submit_validation"], 
                           updates["geo_game_duration_display"],
                           updates["geo_game_score_base_display"], 
                           updates["geo_game_score_bonus_display"], 
                           updates["geo_game_id"]))
    
    # Commit update
    conn.commit()

    if updates["geo_game_submit_lat"] and updates["geo_game_submit_lng"]:

        # Set query
        query = "UPDATE games_geofinder SET "
        query = query + "geo_game_submit_coor = ST_SetSRID(ST_MakePoint(%s, %s), 4326) "
        query = query + "WHERE geo_game_id = %s; "

        # Run query
        cursor.execute(query, (updates["geo_game_submit_lng"], 
                               updates["geo_game_submit_lat"], 
                               updates["geo_game_id"]))

        # Commit update
        conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_geo_game_deleted(db, geo_game_id):

    # TODO try-catch db connection
    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Delete game record on games table
    query = "DELETE FROM games_geofinder WHERE geo_game_id = %s; "
    cursor.execute(query, (geo_game_id,))

    # Commit update
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_geo_game_results(db, geo_game_id):

    # Set game start time
    # TODO All times default to CST
    now = datetime.now()

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            g.*,
            gg.*,
            l.loc_key_lat,
            l.loc_key_lng
        FROM geofinder AS g 
        JOIN games_geofinder AS gg ON g.geofinder_id = gg.geo_game_geofinder_id 
        JOIN locations AS l ON g.geofinder_locations_id = l.id 
        WHERE gg.geo_game_id = %s; 
        """

    # Run query
    cursor.execute(query, (geo_game_id,))

    results = cursor.fetchone()

    # Commit insert
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_geo_game_reviewed(db, user_id, geofinder_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get location info
    query = """
        SELECT * 
        FROM geofinder AS g
        JOIN locations AS l ON g.geofinder_locations_id = l.id
        WHERE g.geofinder_id = %s;
        """
    cursor.execute(query, (geofinder_id,))
    location_info = cursor.fetchone()

    location_id = location_info["id"]

    # GET LOCATIONS_RIGHT
    # geo_game_id (exists) - submitted (1 = yes) - validation (1 = right)
    query = """
        SELECT 
            geo_game_submit_lat, 
            geo_game_submit_lng 
        FROM games_geofinder 
        WHERE geo_game_user_id = %s 
        AND geo_game_geofinder_id = %s 
        AND geo_game_submit_lat IS NOT NULL 
        AND geo_game_submit_lng IS NOT NULL 
        AND geo_game_submit_validation = 1;
        """
    cursor.execute(query, (user_id, geofinder_id,))
    locations_right = cursor.fetchone()

    try:
        locations_right = [{key: value for key, value in locations_right.items()}]
    except AttributeError:
        locations_right = []
    
    # GET LOCATIONS_WRONG
    # geo_game_id (exists) - submitted (1 = yes) - validation (0 = wrong)
    query = """
        SELECT 
            geo_game_submit_lat, 
            geo_game_submit_lng 
        FROM games_geofinder 
        WHERE geo_game_user_id = %s 
        AND geo_game_geofinder_id = %s 
        AND geo_game_submit_lat IS NOT NULL 
        AND geo_game_submit_lng IS NOT NULL 
        AND geo_game_submit_validation = 0;
        """
    cursor.execute(query, (user_id, geofinder_id,))
    locations_wrong = cursor.fetchall()
    locations_wrong = [{key: value for key, value in row.items()} for row in locations_wrong]

    try:
        locations_wrong = [{key: value for key, value in row.items()} for row in locations_wrong]
    except AttributeError:
        locations_wrong = []

    # GET LOCATIONS_NONE
    # geo_game_id (exists) - submitted (0 = no)
    query = """
        SELECT 
            count(*) as count
        FROM games_geofinder 
        WHERE geo_game_user_id = %s 
        AND geo_game_geofinder_id = %s 
        AND geo_game_submit = 0 
        AND geo_game_submit_validation != 2;
        """
    cursor.execute(query, (user_id, geofinder_id))
    locations_none = cursor.fetchone()

    # GET LOCATIONS_QUIT
    # geo_game_id (exists) - submitted (1 = yes) - validation (2 = quit)
    query = """
        SELECT 
            l.loc_key_lat,
            l.loc_key_lng
        FROM geofinder AS g 
        JOIN locations AS l ON g.geofinder_locations_id = l.id 
        JOIN games_geofinder AS gg ON g.geofinder_id = gg.geo_game_geofinder_id 
        WHERE gg.geo_game_user_id = %s
        AND g.geofinder_id = %s 
        AND gg.geo_game_submit_validation = 2;
        """
    cursor.execute(query, (user_id, geofinder_id))
    locations_quit = cursor.fetchall()
    
    try:
        locations_quit = [{key: value for key, value in row.items()} for row in locations_quit]
    except:
        locations_quit = []

    # Get total duration
    query = """
        SELECT 
            TO_CHAR(MAX(geo_game_end) - MIN(geo_game_start), 'HH24:MI:SS') as duration
        FROM games_geofinder 
        WHERE geo_game_user_id = %s
        AND geo_game_geofinder_id = %s
        GROUP BY geo_game_user_id, geo_game_geofinder_id
        ORDER BY geo_game_user_id, geo_game_geofinder_id;
        """
    cursor.execute(query, (user_id, geofinder_id))
    time_clock = cursor.fetchone()

    # Get offset latitude to position infowindow on map
    locations_lat_offsets = latitude_offset(float(location_info["loc_view_lat"]), 
                                            float(location_info["loc_view_lng"]))

    locations_shift = []
    shift = 221
    for i in range(locations_none["count"]):
        lat, lng = longitude_offset(float(location_info["loc_view_lat"]), 
                                    float(location_info["loc_view_lng"]), shift)
        
        latlng = {"game_lat": str(lat), "game_lng": str(lng)}
        locations_shift.append(latlng)
        
        i += 1
        shift += 20

    get_geo_game_review = {
        "loc_view_lat": location_info["loc_view_lat"],
        "loc_view_lng": location_info["loc_view_lng"],
        "loc_lat_offsets": locations_lat_offsets,
        "locations_right": locations_right,
        "locations_wrong": locations_wrong,
        "locations_none": locations_shift,
        "locations_quit": locations_quit,
        "geofinder_id": location_info["geofinder_id"],
        "loc_city": location_info["loc_city"],
        "loc_state": location_info["loc_state"],
        "loc_country": location_info["loc_country"],
        "geofinder_date": location_info["geofinder_date"],
        "loc_image_source": location_info["loc_image_source"],
        "loc_url_source": location_info["loc_url_source"],
        "time_clock": time_clock["duration"],
    }
    
    # Close cursor and connection
    cursor.close()
    conn.close()

    return get_geo_game_review

