import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd


def get_dash_kpi_geofinder(db, user_id):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT count(*) AS count
        FROM games_geofinder 
        WHERE geo_game_user_id = %s
        AND geo_game_submit_validation = 1;
    """

    # Run query
    cursor.execute(query, (user_id,))

    # Get results
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results["count"]


def get_dash_kpi_fifty(db, user_id):

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


# OK but needs testing
def get_dash_geofinder_header(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        WITH profile AS 
            (
            WITH cte AS 
                ( 
                SELECT 
                    geo_game_user_id,
                    geo_game_geofinder_id,
                    MIN(geo_game_start) AS geo_game_datetime_min,
                    MAX(geo_game_end) AS geo_game_datetime_max
                FROM games_geofinder 
                WHERE geo_game_user_id = %s
                GROUP BY geo_game_user_id, geo_game_geofinder_id
                ORDER BY geo_game_user_id, geo_game_geofinder_id
                ) 
            SELECT 
                g.*,
                TO_CHAR(c.geo_game_datetime_max - c.geo_game_datetime_min, 'HH24:MI:SS') AS geo_game_duration_total,
                gg.geo_game_submit_validation,
                c.geo_game_datetime_max::date AS last_game,
                EXTRACT(DAY FROM AGE(CURRENT_DATE, c.geo_game_datetime_max)) AS days 
            FROM geofinder AS g 
            LEFT JOIN cte AS c ON g.geofinder_id = c.geo_game_geofinder_id 
            LEFT JOIN games_geofinder AS gg ON c.geo_game_datetime_max =  gg.geo_game_end
            WHERE g.geofinder_date <= (CURRENT_TIMESTAMP AT TIME ZONE 'US/Central')::date 
            AND g.geofinder_date >= (SELECT date_add::date as date FROM users WHERE id = %s)
            ORDER BY g.geofinder_date DESC
            )
        SELECT 
            * 
        FROM profile AS p; 
        """

    # Run query
    cursor.execute(query, (user_id, user_id,))

    # Get data
    data = cursor.fetchall()

    # Initialize results
    results = {
        "total_found": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "fastest_time": 0,
        "last_game": None,
        "days": None
    }

    if (len(data) > 0):
        # Get results
        df = pd.DataFrame(data)

        # Total Count
        try:
            df_total = df.copy()
            df_total = df_total[df_total['geo_game_submit_validation'] == 1]
            total_count =  df_total['geo_game_submit_validation'].value_counts().iloc[0]
        except:
            total_count = 0

        # Current Streak
        try:
            df_current = df.copy()

            # Remove first row if geo_game_submit_validation is null
            if pd.isnull(df_current.loc[0, 'geo_game_submit_validation']):
                df_current = df_current.drop(df_current.index[0]).reset_index(drop=True)

            # Remove first row if not yet found or quit
            if df_current['geo_game_submit_validation'].iloc[0] == 0:
                df_current.iloc[1:]
            else:
                df_current

            # Get current streak
            if df_current['geo_game_submit_validation'].nunique() == 1:
                current_streak = df_current['geo_game_submit_validation'].sum()
            else:
                current_streak = (df_current['geo_game_submit_validation'] != 1).argmax()

        except:
            current_streak = 0

        # Longest Streak
        try:
            df_longest = df.copy()

            df_longest['geo_game_submit_validation'] = df_longest['geo_game_submit_validation'].fillna(0)
            df_longest['group'] = (df_longest['geo_game_submit_validation'] != df_longest['geo_game_submit_validation'].shift()).cumsum()

            longest_streak = df_longest[df_longest['geo_game_submit_validation'] == 1]['group'].value_counts().max()
            
            try:
                longest_streak = int(longest_streak)
            except:
                longest_streak = 0

        except:
            longest_streak = 0


        # Fastest Time 
        try:
            df_fastest = df.copy()

            df_fastest = df_fastest[df_fastest['geo_game_submit_validation'] == 1]

            df_fastest = df_fastest.dropna(subset=['geo_game_duration_total'])

            if len(df_fastest) > 0:

                df_fastest['geo_game_duration_total'] = pd.to_datetime(df_fastest['geo_game_duration_total'], format='%H:%M:%S', errors='coerce').dt.time

                fastest_time = df_fastest['geo_game_duration_total'].min()
            
            else:

                fastest_time = None

        except:
            fastest_time = None

        # Last Game
        try:
            df_game = df.copy()

            df_game = df_game[df_game['last_game'].notna()]

            if len(df_game) > 0:
                last_game = df_game['last_game'].max()
            else:
                last_game = None
            
        except:
            days = None

        # Days
        try:
            df_days = df.copy()

            df_days = df_days[df_days['days'].notna()]

            if len(df_days) > 0:
                days = df_fastest['days'].min()
            else:
                days = None
            
        except:
            days = None

        # Update results
        results["total_found"] = total_count
        results["current_streak"] = int(current_streak)
        results["longest_streak"] = longest_streak
        results["fastest_time"] = fastest_time
        results["last_game"] = last_game
        results["days"] = days
    
    # Close cursor and connection
    cursor.close()
    conn.close()

    return(results)


def get_dash_geofinder_content(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        WITH cte AS 
            ( 
            SELECT 
                geo_game_user_id,
                geo_game_geofinder_id,
                MIN(geo_game_start) AS geo_game_datetime_min,
                MAX(geo_game_end) AS geo_game_datetime_max
            FROM games_geofinder 
            WHERE geo_game_user_id = %s
            GROUP BY geo_game_user_id, geo_game_geofinder_id
            ORDER BY geo_game_user_id, geo_game_geofinder_id
            ) 
        SELECT 
            g.*,
            c.*,
            TO_CHAR(c.geo_game_datetime_max - c.geo_game_datetime_min, 'HH24:MI:SS') AS geo_game_duration_total,
            gg.*,
            l.loc_city,
            l.loc_state,
            l.loc_country
        FROM geofinder AS g 
        LEFT JOIN cte AS c ON g.geofinder_id = c.geo_game_geofinder_id 
        LEFT JOIN games_geofinder AS gg ON c.geo_game_datetime_max =  gg.geo_game_end
        JOIN locations AS l ON g.geofinder_locations_id = l.id 
        WHERE g.geofinder_date <= (CURRENT_TIMESTAMP AT TIME ZONE 'US/Central')::date 
        AND g.geofinder_date >= (SELECT date_add::date FROM users WHERE id = %s)
        ORDER BY g.geofinder_date DESC
        ; 
        """

    # Run query
    cursor.execute(query, (user_id, user_id,))

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_dash_fifty_header(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            COALESCE(SUM(CASE WHEN fifty_game_submit_validation > 0 THEN 1 ELSE 0 END), 0) AS user_count_loc, 
            COALESCE(SUM(CASE WHEN fifty_game_submit_validation > 0 THEN (fifty_game_score_base + fifty_game_score_bonus) ELSE 0 END), 0) AS user_score_total, 
            COALESCE(SUM(CASE WHEN fifty_game_submit_validation > 0 THEN 1 ELSE 0 END) * 100, 0) AS user_score_possible, 
            CASE WHEN SUM(CASE WHEN fifty_game_submit_validation > 0 THEN 1 ELSE 0 END) > 0 
                THEN ROUND(SUM(CASE WHEN fifty_game_submit_validation > 0 THEN (fifty_game_score_base + fifty_game_score_bonus) ELSE 0 END) / SUM(CASE WHEN fifty_game_submit_validation > 0 THEN 1 ELSE 0 END), 1) 
                ELSE 0 
                END AS user_score_percentage, 
            COALESCE(SUM(fifty_game_duration), 0) AS user_duration_total, 
            COALESCE(AVG(fifty_game_duration), 0) AS user_duration_average, 
            COALESCE(ROUND(SUM(fifty_game_submit_off)::NUMERIC / count(*)), 0) AS user_offset_avg, 
            TO_CHAR(MAX(fifty_game_end), 'YYYY-MM-DD') AS last_game, 
            EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(fifty_game_end))) AS days 
        FROM games_fifty
        WHERE fifty_game_user_id = %s; 
        """

    # Run query
    cursor.execute(query, (user_id,))
    
    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


def get_dash_fifty_content(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        WITH cte AS 
            ( 
            SELECT 
                DISTINCT fifty_game_loc_id 
                ,CASE WHEN sum(fifty_game_submit_validation) OVER (PARTITION BY fifty_game_loc_id) > 1 THEN 'N' WHEN (fifty_game_score_base + fifty_game_score_bonus) = 0 THEN '-' ELSE 'Y' END AS found 
                ,sum(fifty_game_submit_validation) OVER (PARTITION BY fifty_game_loc_id) AS total_game_answer_validation 
                ,count(*) OVER (PARTITION BY fifty_game_loc_id) AS total_attempts 
                ,sum(fifty_game_duration) OVER (PARTITION BY fifty_game_loc_id) AS total_duration 
                ,sum(fifty_game_duration) OVER (PARTITION BY fifty_game_loc_id) / count(*) OVER (PARTITION BY fifty_game_loc_id) AS avg_time 
                ,sum(fifty_game_submit_off) OVER (PARTITION BY fifty_game_loc_id) / count(*) OVER (PARTITION BY fifty_game_loc_id) AS avg_offset 
                ,sum((fifty_game_score_base + fifty_game_score_bonus)) OVER (PARTITION BY fifty_game_loc_id) AS score 
                ,l.loc_city 
                ,l.loc_state 
                ,l.loc_country 
            FROM games_fifty AS gf
            JOIN locations AS l ON gf.fifty_game_loc_id = l.id 
            WHERE fifty_game_user_id = %s
            ORDER BY fifty_game_loc_id 
            ) 
        SELECT * 
        FROM cte 
        WHERE NOT (found = '-' AND score > 0); 
        """

    # Run query
    cursor.execute(query, (user_id,))

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


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


