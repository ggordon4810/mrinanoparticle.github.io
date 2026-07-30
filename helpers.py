"""
Helper functions used by app.py.

This file contains reusable functions for:
- connecting to the SQLite database
- creating the required database tables
- running database queries
- converting optional form values into numbers
"""

import sqlite3


DATABASE_PATH = "nanomri.db"


def get_db_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the database tables if they do not already exist.
    """

    connection = get_db_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sample_type TEXT,
            description TEXT,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS relaxivity_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            relaxivity REAL NOT NULL,
            intercept REAL NOT NULL,
            r_squared REAL NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experiment_id)
                REFERENCES experiments (id)
                ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS relaxivity_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            concentration REAL NOT NULL,
            t1 REAL NOT NULL,
            r1 REAL NOT NULL,
            FOREIGN KEY (result_id)
                REFERENCES relaxivity_results (id)
                ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS dls_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            z_average_nm REAL NOT NULL,
            pdi REAL NOT NULL,
            intensity_size_nm REAL,
            volume_size_nm REAL,
            number_size_nm REAL,
            recommended_value TEXT NOT NULL,
            interpretation TEXT NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experiment_id)
                REFERENCES experiments (id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()

    connection.close()


def fetch_all(query, parameters=()):

    connection = get_db_connection()

    rows = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return rows


def fetch_one(query, parameters=()):

    connection = get_db_connection()

    row = connection.execute(
        query,
        parameters
    ).fetchone()

    connection.close()

    return row


def execute_query(query, parameters=()):

    connection = get_db_connection()

    cursor = connection.execute(
        query,
        parameters
    )

    connection.commit()

    inserted_id = cursor.lastrowid

    connection.close()

    return inserted_id


def parse_optional_float(value, field_name):
    if value is None or value.strip() == "":
        return None

    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{field_name} must be a valid number.")
        


def parse_required_float(value, field_name):

    if value is None or str(value).strip() == "":
        raise ValueError(
            f"{field_name} is required."
        )

    try:
        return float(value)

    except ValueError:
        raise ValueError(
            f"{field_name} must be a valid number."
        )


def parse_number_list(text, field_name):

    if text is None or text.strip() == "":
        raise ValueError(
            f"{field_name} is required."
        )

    pieces = text.split(",")

    values = []

    for piece in pieces:
        cleaned_piece = piece.strip()

        if cleaned_piece == "":
            raise ValueError(
                f"{field_name} contains an empty value."
            )

        try:
            number = float(cleaned_piece)

        except ValueError:
            raise ValueError(
                f"{field_name} must contain only numbers separated by commas."
            )

        values.append(number)

    return values
