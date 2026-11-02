
import sqlite3
import pandas as pd

DATABASE_NAME = "ecobin.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    """Create and return a SQLite database connection."""
    return sqlite3.connect(DATABASE_NAME)


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def init_database():
    """Create the required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Table for sustainable actions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            category TEXT NOT NULL,
            action_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            points INTEGER NOT NULL,
            notes TEXT
        )
    """)

    # Table for completed daily challenges
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completed_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_title TEXT NOT NULL,
            completion_date TEXT NOT NULL,
            points INTEGER NOT NULL,
            UNIQUE(challenge_title, completion_date)
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# ADD A SUSTAINABLE ACTION
# --------------------------------------------------

def add_action(action, category, action_date, quantity, points, notes=""):
    """Save a sustainable action."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO actions (
            action,
            category,
            action_date,
            quantity,
            points,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        action,
        category,
        action_date,
        quantity,
        points,
        notes
    ))

    connection.commit()
    connection.close()


# --------------------------------------------------
# GET ALL ACTIONS
# --------------------------------------------------

def get_all_actions():
    """Return all recorded actions as a DataFrame."""

    connection = get_connection()

    query = """
        SELECT
            id,
            action,
            category,
            action_date,
            quantity,
            points,
            notes
        FROM actions
        ORDER BY action_date DESC, id DESC
    """

    dataframe = pd.read_sql_query(query, connection)

    connection.close()

    return dataframe


# --------------------------------------------------
# CALCULATE TOTAL POINTS
# --------------------------------------------------

def get_total_points():
    """Calculate total points earned from all activities."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(points), 0)
        FROM actions
    """)

    total_points = cursor.fetchone()[0]

    connection.close()

    return total_points


# --------------------------------------------------
# CATEGORY SUMMARY
# --------------------------------------------------

def get_category_summary():
    """Calculate activity totals for each category."""

    connection = get_connection()

    query = """
        SELECT
            category,
            SUM(quantity) AS total
        FROM actions
        GROUP BY category
        ORDER BY total DESC
    """

    dataframe = pd.read_sql_query(query, connection)

    connection.close()

    return dataframe


# --------------------------------------------------
# DAILY ACTIVITY SUMMARY
# --------------------------------------------------

def get_daily_summary():
    """Return daily points and activity totals."""

    connection = get_connection()

    query = """
        SELECT
            action_date,
            SUM(points) AS total_points,
            COUNT(*) AS total_actions
        FROM actions
        GROUP BY action_date
        ORDER BY action_date DESC
    """

    dataframe = pd.read_sql_query(query, connection)

    connection.close()

    return dataframe


# --------------------------------------------------
# COMPLETE A DAILY CHALLENGE
# --------------------------------------------------

def complete_challenge(challenge_title, completion_date, points):
    """
    Save a completed challenge.

    Returns True if saved successfully.
    Returns False if the challenge was already completed that day.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO completed_challenges (
                challenge_title,
                completion_date,
                points
            )
            VALUES (?, ?, ?)
        """, (
            challenge_title,
            completion_date,
            points
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


# --------------------------------------------------
# CHECK CHALLENGE COMPLETION
# --------------------------------------------------

def has_completed_challenge(challenge_title, completion_date):
    """Check whether a challenge has already been completed."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM completed_challenges
        WHERE challenge_title = ?
        AND completion_date = ?
    """, (
        challenge_title,
        completion_date
    ))

    result = cursor.fetchone()

    connection.close()

    return result is not None


# --------------------------------------------------
# GET COMPLETED CHALLENGES
# --------------------------------------------------

def get_completed_challenges(completion_date=None):
    """Retrieve completed challenges, optionally for a specific date."""

    connection = get_connection()

    if completion_date:
        query = """
            SELECT
                challenge_title,
                completion_date,
                points
            FROM completed_challenges
            WHERE completion_date = ?
            ORDER BY id DESC
        """

        dataframe = pd.read_sql_query(
            query,
            connection,
            params=(completion_date,)
        )

    else:
        query = """
            SELECT
                challenge_title,
                completion_date,
                points
            FROM completed_challenges
            ORDER BY completion_date DESC, id DESC
        """

        dataframe = pd.read_sql_query(query, connection)

    connection.close()

    return dataframe

