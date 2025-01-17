# Third-Party Libraries
import psycopg2
from psycopg2.extras import RealDictCursor





# authy
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


# authy
def get_registered(db, new_username, new_password):

    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Set query
    query = "INSERT INTO users (username, hash) "
    query = query + "VALUES (%s, %s); "

    # Run and commitquery
    try:
        cursor.execute(query, (new_username, new_password))
        conn.commit()
        results = 1
    except psycopg2.errors.UniqueViolation as e:
        results = e

    cursor.close()
    conn.close()

    return results


# profile
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


# profile
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


# profile
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


# profile
def get_dash_main(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT id, username, date_add, country, icon 
        FROM users 
        WHERE id = %s; 
        """

    # Run query
    cursor.execute(query, (user_id,))
    
    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


# profile
def get_dash_main_updated_username(db, username, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        UPDATE users SET 
            username = %s, 
            date_updated = CURRENT_TIMESTAMP 
        WHERE id = %s; 
        """
    
    # Run query
    cursor.execute(query, (username, id))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1


# profile
def get_dash_main_updated_country(db, country, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        UPDATE users SET 
            country = %s, 
            date_updated = CURRENT_TIMESTAMP 
        WHERE id = %s; 
        """

    # Run query
    cursor.execute(query, (country, id))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1


# profile
def get_dash_main_updated_hash(db, password, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        UPDATE users SET 
            hash = %s, 
            date_updated = CURRENT_TIMESTAMP 
        WHERE id = %s; 
        """

    # Run query
    cursor.execute(query, (password, id))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1

