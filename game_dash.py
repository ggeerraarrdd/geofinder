import psycopg2
from psycopg2.extras import RealDictCursor


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

