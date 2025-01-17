# Python Standard Library
from datetime import datetime, timezone
from math import ceil, exp

# Third-Party Libraries
import psycopg2
from psycopg2.extras import RealDictCursor
import pytz
import shapely.wkb
from shapely.geometry import Point

# Local
from helpers import get_duration, get_distance, latitude_offset, longitude_offset





def get_fifty_kpi(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            COALESCE(ROUND(SUM((fifty_game_score_base + fifty_game_score_bonus))::NUMERIC / COUNT(*), 1), 0) AS user_summary_percent
        FROM games_fifty
        WHERE fifty_game_submit_validation > 0 
        AND fifty_game_user_id = %s; 
        """

    # Run query
    cursor.execute(query, (user_id,))

    # Get results
    results = cursor.fetchone()

    # Process results
    try:
        results = int(results["user_summary_percent"])
    except TypeError:
        results = 0

    cursor.close()
    conn.close()

    return results


def get_fifty_package_dash_header(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query 1
    query1 = """
        SELECT 
            CASE WHEN SUM(CASE WHEN fifty_game_submit_validation > 0 THEN 1 ELSE 0 END) > 0 
                THEN ROUND(SUM(CASE WHEN fifty_game_submit_validation > 0 THEN (fifty_game_score_base + fifty_game_score_bonus) ELSE 0 END) / SUM(CASE WHEN fifty_game_submit_validation > 0 THEN 1 ELSE 0 END), 1) 
                ELSE 0 
                END AS user_score_percentage, 
            COALESCE(SUM(CASE WHEN fifty_game_submit_validation > 0 THEN (fifty_game_score_base + fifty_game_score_bonus) ELSE 0 END), 0) AS user_score_total, 
            COALESCE(SUM(CASE WHEN fifty_game_submit_validation > 0 THEN 1 ELSE 0 END) * 100, 0) AS user_score_possible, 
            COALESCE(SUM(CASE WHEN fifty_game_submit_validation = 1 THEN 1 ELSE 0 END), 0) AS user_loc_found, 
            COALESCE(ROUND(SUM(fifty_game_submit_off)::NUMERIC / SUM(fifty_game_submit)::NUMERIC), 0) AS user_offset_avg, 
            TO_CHAR(MAX(fifty_game_end), 'YYYY-MM-DD') AS last_game, 
            EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(fifty_game_end))) AS days 
        FROM games_fifty
        WHERE fifty_game_user_id = %s; 
        """

    # Run query 1
    cursor.execute(query1, (user_id,))

    # Get results 1
    results1 = cursor.fetchone()

    # Set query 2
    query2 = """
        WITH cte AS 
        (
        SELECT 
            DISTINCT fifty_game_loc_id 
            ,MIN(fifty_game_start) OVER (PARTITION BY fifty_game_loc_id) AS min_start
            ,MAX(fifty_game_end) OVER (PARTITION BY fifty_game_loc_id) AS max_end
        FROM games_fifty
        WHERE fifty_game_user_id = %s
        AND fifty_game_is_void IS FALSE
        AND fifty_game_submit IS NOT NULL 
        )
    SELECT 
        COALESCE(TO_CHAR(max_end - min_start, 'HH24:MI:SS'), '--') AS fifty_game_duration_total_str
    FROM locations AS l
    LEFT JOIN cte AS c ON l.id = c.fifty_game_loc_id
    LEFT JOIN games_fifty AS gf ON c.fifty_game_loc_id = gf.fifty_game_loc_id AND c.max_end = gf.fifty_game_end 
    WHERE l.loc_game = 'geo50x'
    AND gf.fifty_game_submit_validation = 1
    ORDER BY fifty_game_duration_total_str
    LIMIT 1
    ;
    """

    # Run query 2
    cursor.execute(query2, (user_id,))

    # Get results 2
    results2 = cursor.fetchone()

    try:
        fastest = results2["fifty_game_duration_total_str"]
    except:
        fastest = '--'

    cursor.close()
    conn.close()

    # Create GAME package
    get_fifty_package_dash_header = {
        "user_score_percentage": results1["user_score_percentage"],
        "user_score_total": results1["user_score_total"],
        "user_score_possible": results1["user_score_possible"],
        "user_loc_found": results1["user_loc_found"],
        "user_offset_avg": results1["user_offset_avg"],
        "last_game": results1["last_game"],
        "days": results1["days"],
        "user_duration_fastest": fastest,
    }

    return get_fifty_package_dash_header


def get_fifty_package_dash_content(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        WITH cte AS 
            (
            SELECT 
                DISTINCT fifty_game_loc_id 
                ,SUM(fifty_game_submit) OVER (PARTITION BY fifty_game_loc_id) AS total_submits
                ,SUM(fifty_game_submit_off) OVER (PARTITION BY fifty_game_loc_id) AS total_submits_off
                ,MIN(fifty_game_start) OVER (PARTITION BY fifty_game_loc_id) AS min_start
                ,MAX(fifty_game_end) OVER (PARTITION BY fifty_game_loc_id) AS max_end
            FROM games_fifty
            WHERE fifty_game_user_id = %s
            AND fifty_game_is_void IS FALSE
            AND fifty_game_submit IS NOT NULL 
            )
        SELECT 
            l.id
            ,l.loc_game 
            ,l.loc_city 
            ,l.loc_state 
            ,l.loc_country 
            ,c.total_submits AS fifty_game_submit_total
            ,c.total_submits_off AS fifty_game_submit_off_total
            ,(c.total_submits_off / c.total_submits) AS fifty_game_submit_off_avg
            ,gf.fifty_game_submit_validation
            ,FLOOR(EXTRACT(EPOCH FROM (c.max_end -c.min_start))) AS fifty_game_duration_total
            ,TO_CHAR(max_end - min_start, 'HH24:MI:SS') AS fifty_game_duration_total_str
            ,fifty_game_score_base + fifty_game_score_bonus AS fifty_game_score_total
            ,CASE WHEN fifty_game_submit_validation > 0 OR c.total_submits >= 6 THEN 0 ELSE 1 END AS fifty_game_loc_available
        FROM locations AS l
        LEFT JOIN cte AS c ON l.id = c.fifty_game_loc_id
        LEFT JOIN games_fifty AS gf ON c.fifty_game_loc_id = gf.fifty_game_loc_id AND c.max_end = gf.fifty_game_end 
        WHERE l.loc_game = 'geo50x'
        ORDER BY l.id
        ;
        """

    # Run query
    cursor.execute(query, (user_id,))

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_fifty_game_loc_playable(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT id
        FROM locations 
        WHERE loc_game = 'geo50x' 
        AND id NOT IN 
            (
            SELECT DISTINCT fifty_game_loc_id 
            FROM games_fifty
            WHERE fifty_game_user_id = %s
            AND fifty_game_submit IS NOT NULL
            AND fifty_game_submit_validation > 0
            ) 
        AND id NOT IN 
            (
            SELECT fifty_game_loc_id
            FROM games_fifty 
            WHERE fifty_game_user_id = %s
            AND fifty_game_submit IS NOT NULL
            AND fifty_game_submit = 1
            GROUP BY fifty_game_loc_id 
            HAVING SUM(fifty_game_submit) >= 6
            )
        AND loc_playable = TRUE 
        ORDER BY random()
        LIMIT 1
        """

    # Run query
    cursor.execute(query, (user_id, user_id,))

    # Get playable locations
    loc = cursor.fetchone()

    cursor.close()
    conn.close()

    try:
        results = loc["id"]
    except:
        results = None

    return results


def get_fifty_game_loc_info(db, loc_id, loc_game):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM locations 
        WHERE id = %s 
        AND loc_game = %s; 
        """
    
    # Run query
    cursor.execute(query, (loc_id, loc_game,))
    
    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


def get_fifty_game_loc_submits(db, user_id, loc_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            fifty_game_loc_id 
            ,COALESCE(SUM(fifty_game_submit), 0) AS total_submits
        FROM games_fifty
        WHERE fifty_game_user_id = %s
        AND fifty_game_loc_id = %s
        AND fifty_game_is_void IS FALSE
        AND fifty_game_submit IS NOT NULL 
        GROUP BY fifty_game_loc_id
        ;
        """
    
    # Run query
    cursor.execute(query, (user_id, loc_id,))
    
    # Get results
    results = cursor.fetchone()

    try:
        results = results["total_submits"]
    except:
        results = None

    cursor.close()
    conn.close()

    return results


def get_fifty_game_started(db, user_id, loc_id, now):
    
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

    return results


def get_fifty_game_duration_total(db, user_id, loc_id, now):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            TO_CHAR(%s - MIN(fifty_game_start), 'HH24:MI:SS') AS duration_total_time
            ,EXTRACT(EPOCH FROM MAX(fifty_game_end) - MIN(fifty_game_start)) AS duration_total_secs
        FROM games_fifty
        WHERE fifty_game_user_id = %s
        AND fifty_game_loc_id = %s
        AND fifty_game_is_void IS FALSE
        GROUP BY fifty_game_loc_id 
        ;
        """

    # Run query
    cursor.execute(query, (now, user_id, loc_id))

    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


def get_fifty_game_score(db, user_id, location_id, validation, duration):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT count(*) AS count 
        FROM games_fifty 
        WHERE fifty_game_user_id = %s 
        AND fifty_game_loc_id = %s
        AND fifty_game_submit IS NOT NULL;
        """

    # Run query
    cursor.execute(query, (user_id, location_id))

    # Get pre-results
    pre_results = cursor.fetchone()

    # Get attempts from pre-results
    attempts = int(pre_results["count"]) + 1

    # TODO Calculate total duration of all attempts
    
    # Calculate score
    if validation == 1:
        
        # Calculate base
        if attempts <= 1:
            base = 50
        elif attempts == 2:
            base = 40
        elif attempts == 3:
            base = 30
        elif attempts == 4:
            base = 20
        elif attempts == 5:
            base = 10
        else:
            base = 0

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


def get_fifty_package_game(db, user_id):

    # Get time
    now = datetime.now(timezone.utc).astimezone(pytz.timezone('US/Central'))

    # Get loc playable
    loc_id = get_fifty_game_loc_playable(db, user_id)

    # Get loc submits
    submits = get_fifty_game_loc_submits(db, user_id, loc_id)

    if loc_id:

        # Get loc info
        loc = get_fifty_game_loc_info(db, loc_id, "geo50x")

        # Get loc started
        fifty_game_id = get_fifty_game_started(db, user_id, loc_id, now)

        # Get lat offset
        loc_lat_game_offset = latitude_offset(float(loc["loc_view_lat"]), 
                                              float(loc["loc_view_lng"]))

        # Create GAME package
        get_fifty_package_game = {
            "fifty_game_id": fifty_game_id["fifty_game_id"],
            "fifty_game_submit_total": submits,
            "fifty_game_loc_id": loc_id,
            "fifty_game_start": now,
            "fifty_game_loc_url_source": loc["loc_url_source"],
            "fifty_game_loc_view_lat": loc["loc_view_lat"],
            "fifty_game_loc_view_lng": loc["loc_view_lng"],
            "fifty_game_loc_key_lat": loc["loc_key_lat"],
            "fifty_game_loc_key_lng": loc["loc_key_lng"],
            "fifty_game_loc_key_shp": loc["loc_key_shp"],
            "fifty_game_loc_image_source": loc["loc_image_source"],
            "fifty_game_loc_city": loc["loc_city"],
            "fifty_game_loc_state": loc["loc_state"],
            "fifty_game_loc_country": loc["loc_country"],
            "fifty_game_loc_lat_game_offset": loc_lat_game_offset,
            "fifty_game_clock": { "hour": now.hour, "minute": now.minute, "second": now.second },
        }

    else:
        get_fifty_package_game = None

    return get_fifty_package_game


def get_fifty_package_game_again(db, user_id, loc_id):

    # Get time
    now = datetime.now(timezone.utc).astimezone(pytz.timezone('US/Central'))

    # Get loc info
    loc = get_fifty_game_loc_info(db, loc_id, "geo50x")

    # Get loc submits
    submits = get_fifty_game_loc_submits(db, user_id, loc_id)

    # Get loc started
    fifty_game_id = get_fifty_game_started(db, user_id, loc_id, now)

    # Get lat offset
    loc_lat_game_offset = latitude_offset(float(loc["loc_view_lat"]), 
                                            float(loc["loc_view_lng"]))

    # Create GAME package
    fifty_package_game = {
        "fifty_game_id": fifty_game_id["fifty_game_id"],
        "fifty_game_submit_total": submits,
        "fifty_game_loc_id": loc_id,
        "fifty_game_start": now,
        "fifty_game_loc_url_source": loc["loc_url_source"],
        "fifty_game_loc_view_lat": loc["loc_view_lat"],
        "fifty_game_loc_view_lng": loc["loc_view_lng"],
        "fifty_game_loc_key_lat": loc["loc_key_lat"],
        "fifty_game_loc_key_lng": loc["loc_key_lng"],
        "fifty_game_loc_key_shp": loc["loc_key_shp"],
        "fifty_game_loc_image_source": loc["loc_image_source"],
        "fifty_game_loc_city": loc["loc_city"],
        "fifty_game_loc_state": loc["loc_state"],
        "fifty_game_loc_country": loc["loc_country"],
        "fifty_game_loc_lat_game_offset": loc_lat_game_offset,
        "fifty_game_clock": { "hour": now.hour, "minute": now.minute, "second": now.second },
    }

    return fifty_package_game


def get_fifty_package_results(db, user_id, package, submit, submit_lat, submit_lng, lat_display, lng_display):

    # Get time
    now = datetime.now(timezone.utc).astimezone(pytz.timezone('US/Central'))

    # Get duration of game for loc
    duration_game = get_duration(package["fifty_game_start"], now)

    # Get duration of all games for loc
    duration = get_fifty_game_duration_total(db, 
                                             user_id, 
                                             package["fifty_game_loc_id"],
                                             now)

    if submit == 0:
    
        fifty_game_submit_off = None
        fifty_game_submit_validation = 2

    else:
        # Convert the PostGIS geometry into a Shapely geometry object
        polygon = shapely.wkb.loads(package["fifty_game_loc_key_shp"], hex=True)

        # Create a point object from user submitted (lat, lng)
        point = Point([submit_lng, submit_lat])

        # Update package
        fifty_game_submit_off = get_distance(point, polygon)

        # Check if point is inside polygon
        is_inside = polygon.contains(point)

        # Validate answer as 1 = "correct"
        if is_inside:

            fifty_game_submit_validation = 1

        else:

            fifty_game_submit_validation = 0
        
    # Calculate game score
    scores = get_fifty_game_score(db, 
                                  user_id, 
                                  package["fifty_game_loc_id"], 
                                  fifty_game_submit_validation, 
                                  duration["duration_total_secs"])
    
    # Create RESULTS package
    fifty_package_results = {
        "fifty_game_id": package["fifty_game_id"],
        "fifty_game_start": package["fifty_game_start"],
        "fifty_game_end": now,
        "fifty_game_loc_id": package["fifty_game_loc_id"],
        "fifty_game_loc_url_source": package["fifty_game_loc_url_source"],
        "fifty_game_loc_view_lat": package["fifty_game_loc_view_lat"],
        "fifty_game_loc_view_lng": package["fifty_game_loc_view_lng"],
        "fifty_game_loc_key_lat": package["fifty_game_loc_key_lat"],
        "fifty_game_loc_key_lng": package["fifty_game_loc_key_lng"],
        "fifty_game_loc_key_shp": package["fifty_game_loc_key_shp"],
        "fifty_game_loc_image_source": package["fifty_game_loc_image_source"],
        "fifty_game_loc_city": package["fifty_game_loc_city"],
        "fifty_game_loc_state": package["fifty_game_loc_state"],
        "fifty_game_loc_country": package["fifty_game_loc_country"],
        "fifty_game_loc_lat_game_offset": package["fifty_game_loc_lat_game_offset"],
        "fifty_game_submit": submit,
        "fifty_game_submit_lat": submit_lat,
        "fifty_game_submit_lng": submit_lng,
        "fifty_game_submit_lat_display": lat_display,
        "fifty_game_submit_lng_display": lng_display,
        "fifty_game_submit_off": fifty_game_submit_off,
        "fifty_game_submit_validation": fifty_game_submit_validation,
        "fifty_game_submit_attempts": scores["attempts"],
        "fifty_game_duration_display": duration_game,
        "fifty_game_duration_total_display": duration["duration_total_time"],
        "fifty_game_score_base_display": scores["base"],
        "fifty_game_score_bonus_display": scores["bonus"],
        "fifty_game_score_total_display": scores["total"]
    }

    return fifty_package_results


def get_fifty_package_review(db, user_id, loc_id, time, score):

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

    # Get loc key
    if len(locations_right) == 0:
        query = """
            SELECT 
                loc_key_lat AS game_lat, 
                loc_key_lng AS game_lng 
            FROM locations
            WHERE id = %s;
            """
        cursor.execute(query, (loc_id,))
        locations_key = cursor.fetchall()

        print(locations_key)
        
        try:
            locations_key = [{key: value for key, value in row.items()} for row in locations_key]
        except AttributeError:
            locations_key = []
    
    else:
        locations_key = []

    # Get offset latitude to position infowindow on map
    loc_lat_game_offset = latitude_offset(float(loc_info["loc_view_lat"]), float(loc_info["loc_view_lng"]))

    locations_shift = []
    shift = 221
    for i in range(6 - len(locations_wrong) - len(locations_right)):
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
        "locations_key": locations_key,
        "loc_city": loc_info["loc_city"],
        "loc_state": loc_info["loc_state"],
        "loc_country": loc_info["loc_country"],
        "loc_image_source": loc_info["loc_image_source"],
        "loc_url_source": loc_info["loc_url_source"],
        "time_clock": time,
        "score": score
    }

    # Close cursor and connection
    cursor.close()
    conn.close()

    return get_fifty_game_review

