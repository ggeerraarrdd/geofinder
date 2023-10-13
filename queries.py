from cs50 import SQL
import sqlite3
from random import randint
from datetime import datetime
from math import floor, ceil, exp
from haversine import haversine, Unit


def get_user(db, new_username, new_password):
    
    # Create connection and cursor
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (new_username, new_password))

    # Commit insert
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

    return 0

def get_user_info(db, user_id):

    # Create connection and cursor
    connection = sqlite3.connect(db, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = "SELECT * "
    query = query + "FROM users "
    query = query + "WHERE username = ?; "
    cursor.execute(query, (user_id,))
    user_info = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    connection.close()

    return(user_info)


def get_total_score(db, user_id):

    # Create connection and cursor
    connection = sqlite3.connect(db, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = "SELECT sum(game_score) AS total FROM games WHERE user_id = ?; "
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    try:
        total = int(result["total"])
    except TypeError:
        total = 0

    # Close cursor and connection
    cursor.close()
    connection.close()

    return total


def get_playable_location(db, user_id):

    # Print to debug
    # print(user_id)

    # Create connection and cursor
    connection = sqlite3.connect(db, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Get playable locations
    query = "SELECT * "
    query = query + "FROM locs "
    query = query + "WHERE id NOT IN (SELECT DISTINCT loc_id FROM games WHERE user_id = ? AND game_answer_validation = 1) "
    query = query + "AND loc_active = 1; "
    cursor.execute(query, (user_id,))
    locs_playable = cursor.fetchall()
    
    # Get count of playable locations
    locs_playable_count = len(locs_playable)

    # Generate random number in range to loc_playable
    row = randint(0, locs_playable_count - 1)

    # Get row
    location = dict(locs_playable[row])

    cursor.close()
    connection.close()

    return(location)


def get_playable_location_again(db, current_game_id):

    # Create connection and cursor
    connection = sqlite3.connect(db, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Get playable locations
    query = "SELECT * "
    query = query + "FROM locs "
    query = query + "WHERE id = ?; "
    cursor.execute(query, (current_game_id,))
    locs_playable = cursor.fetchone()

    location = dict(locs_playable)

    # Close cursor and connection
    cursor.close()
    connection.close()

    return location


def start_game(db, user_id, loc_id):

    # Set game start time
    # TODO All times default to CST
    now = datetime.now()

    # print(now)

    # Create connection and cursor
    connection = sqlite3.connect(db, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Insert values from get_playable_location to games table
    query = "INSERT INTO games (user_id, loc_id, game_start, game_end) VALUES "
    query = query + "(?, ?, ?, ?); "
    cursor.execute(query, (user_id, loc_id, now, now))

    game_id = cursor.lastrowid

    # Print to debug
    # print("game_id:", game_id)

    # Commit insert
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

    return(game_id, now)


def update_current_game(db, id, game_end, game_lat, game_lng, game_user_quit, game_answer_off, game_answer_validation, game_duration, game_score):

    # (db, id, game_end, game_lat, game_lng, game_user_quit, game_answer_off, game_answer_validation, game_duration, game_score)

    # TODO try-catch db connection
    # Create connection and cursor
    connection = sqlite3.connect(db, check_same_thread=False)
    # connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Update game record on games table
    query = "UPDATE games "
    query = query + "SET game_end = ?, "
    query = query + "game_lat = ?, " 
    query = query + "game_lng = ?, " 
    query = query + "game_user_quit = ?, " 
    query = query + "game_answer_off = ?, "
    query = query + "game_answer_validation = ?, " 
    query = query + "game_duration = ?, "
    query = query + "game_score = ? "
    query = query + "WHERE id = ?; "
    cursor.execute(query, (game_end, game_lat, game_lng, game_user_quit, game_answer_off, game_answer_validation, game_duration, game_score, id))

    game_id = cursor.lastrowid

    # Print to debug
    print("game_id:", game_id)

    # Commit update
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

    return 1


def get_current_game_deleted(db, current_game_id):

    # TODO try-catch db connection
    # Create connection and cursor
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    # Delete game record on games table
    query = "DELETE FROM games WHERE id = ?; "
    cursor.execute(query, (current_game_id,))

    # Commit update
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

    return 1


def game_answer_distance(loc_answer_lat, loc_answer_long, game_answer_lat, game_answer_long):

    # https://pypi.org/project/haversine/
    # https://en.wikipedia.org/wiki/Haversine_formula
    # Calculate distance between answer coordinates and user-submitted coordinates
    # Distance in feet

    answer = (float(loc_answer_lat), float(loc_answer_long))
    submitted = (float(game_answer_lat), float(game_answer_long))

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
    connection = sqlite3.connect(db, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = "SELECT ifnull(sum(game_duration), 0) AS total "
    query = query + "FROM games "
    query = query + "WHERE id != ? "
    query = query + "AND user_id = ? "
    query = query + "AND loc_id = ?; "
    cursor.execute(query, (current_game_id, user_id, loc_id))
    result = cursor.fetchone()
                        
    total = int(result["total"]) + int(current_game_duration)

    # Close cursor and connection
    cursor.close()
    connection.close()

    return total

def game_answer_score(db, user_id, location_id, validation, duration):

    base_score = 0
    bonus_score = 0
    bonus_score_multiplier = 0

    # Create connection and cursor
    connection = sqlite3.connect(db, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Calculate max base score based on attempts
    query = "SELECT count(*) AS count "
    query = query + "FROM games "
    query = query + "WHERE user_id = ? "
    query = query + "AND loc_id = ?; "
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
        bonus_score_multiplier = exp(-0.0054*(duration-1)**2)
        bonus_score = round(50 * bonus_score_multiplier)

    # Calculate game score
    game_score = base_score + bonus_score

    # Print debug
    # print(f"Attempts: {attempts}")
    # print(f"Multiplier: {bonus_score_multiplier}")
    # print(f"Bonus: {bonus_score}")
    # print(f"Score: {game_score}")

    # Close cursor and connection
    cursor.close()
    connection.close()

    return base_score, bonus_score, game_score, attempts


def get_history(db, user_id):

    # Create connection and cursor
    connection = sqlite3.connect(db)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Get history
    query = "WITH cte AS "
    query = query + "( "
    query = query + "SELECT "
    query = query + "DISTINCT loc_id "
    query = query + ",CASE WHEN game_score = 0 THEN '-' ELSE 'yes' END AS found "
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
    query = query + "WHERE user_id = ? "
    query = query + "ORDER BY loc_id "
    query = query + ") "
    query = query + "SELECT * FROM cte WHERE NOT (found = '-' AND score > 0); "
    cursor.execute(query, (user_id,))
    history = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    connection.close()

    return history




