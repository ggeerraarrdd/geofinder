import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from math import ceil
import time


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


# Can be deleted
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


# Used by get_disconnected()
def get_current_game_deleted(db, current_game_id):

    # TODO try-catch db connection
    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Delete game record on games table
    query = "DELETE FROM games_fifty WHERE fifty_game_id = %s; "
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
    
    # Delay function by 6 seconds to allow other functions to update db
    time.sleep(6)

    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Set query
    query = """
        SELECT fifty_game_duration 
        FROM games_fifty 
        WHERE fifty_game_id = %s; 
        """

    # Run query
    cursor.execute(query, (current_game_id,))

    # Get results
    results = cursor.fetchone()

    # Check if game record is deleted or still there
    if results == None: 
        # Game record has been deleted
        results = f"Game record has been deleted."
    
    else:
        # Game record is still there & game_duration is still None
        if results[0] == None:
            # Calculate duration
            duration_sec, duration_min = game_answer_duration(current_game_start, current_game_end)

            if duration_sec >= 10:
                # Update fifty_game_duration
                query = "UPDATE games_fifty SET fifty_game_duration = %s WHERE fifty_game_id = %s; "
                cursor.execute(query, (duration_sec, current_game_id))
                conn.commit()

                results = f"Game record updated."
            
            else:
                # Delete games_fifty record
                query = "DELETE FROM games_fifty WHERE fifty_game_id = %s; "
                cursor.execute(query, (current_game_id,))
                conn.commit()
                
                results = f"Game record deleted."
        
        # Game record is still there & game_duration is still None
        else:
            results = f"Game record has game_duration."

    cursor.close()
    conn.close()

    return results


def get_disconnected_geo(db, current_game_id, current_game_start):

    # Set current timestamp
    current_game_end = datetime.now()
    
    # Delay function by 6 seconds to allow other functions to update db
    time.sleep(6)

    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Set query
    query = """
        SELECT geo_game_duration 
        FROM games_geofinder
        WHERE geo_game_id = %s; 
        """

    # Run query
    cursor.execute(query, (current_game_id,))

    # Get results
    results = cursor.fetchone()

    # Check if game record is deleted or still there
    if results == None: 
        # Game record has been deleted
        results = f"Game record has been deleted."
    
    else:
        # Game record is still there & game_duration is still None
        if results[0] == None:
            # Calculate duration
            duration_sec, duration_min = game_answer_duration(current_game_start, current_game_end)

            if duration_sec >= 10:
                # Update geo_game_duration
                query = "UPDATE games_geofinder SET geo_game_duration = %s WHERE geo_game_id = %s; "
                cursor.execute(query, (duration_sec, current_game_id))
                conn.commit()

                results = f"Game record updated."
            
            else:
                # Delete games_geofinder record
                query = "DELETE FROM games_geofinder WHERE geo_game_id = %s; "
                cursor.execute(query, (current_game_id,))
                conn.commit()
                results = f"Game record deleted."
        
        # Game record is still there & game_duration is still None
        else:
            results = f"Game record has game_duration."

    cursor.close()
    conn.close()
    
    return results


# Used by get_disconnected()
def game_answer_duration(game_start, game_end):

    # Calculate time difference in seconds
    game_duration = game_end - game_start
    duration_sec = game_duration.seconds
    duration_min = ceil(game_duration.seconds / 60)

    return duration_sec, duration_min


# Used by /fifty/game
def get_loc_duration_total(db, current_game_id, user_id, loc_id, current_game_duration):
    
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

