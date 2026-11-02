
import sqlite3
import pandas as pd

DATABASE_NAME = "ecobin.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    """Create and return a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_NAME)
    return connection


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def init_database():
    """Create the actions table if it does not already exist."""

    connection = get_connection()
    cursor = connection.cursor()

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

    connection.commit()
    connection.close()


# --------------------------------------------------
# ADD A SUSTAINABLE ACTION
# --------------------------------------------------

def add_action(action, category, action_date, quantity, points, notes=""):
    """Save a completed sustainable action to the database."""

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
    """Return all recorded actions as a Pandas DataFrame."""

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
    """Calculate the total Eco Points earned."""

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
    """Calculate the total number of recorded actions per category."""

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
    """Return total points earned on each date."""

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
