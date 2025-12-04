import sqlite3

DB_NAME = "queries.db"


def initialize_database():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Create table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY,
                query TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()


def insert_query(query):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO queries (query) VALUES (?)
        """,
            (query,),
        )

        conn.commit()


def fetch_queries():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT query FROM queries ORDER BY date_created DESC LIMIT 50")
        return cursor.fetchall()


def delete_database():
    import os

    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    else:
        print("The database does not exist.")
