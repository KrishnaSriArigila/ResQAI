import sqlite3

DATABASE = "resqai.db"


def create_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            incident_type TEXT,
            severity TEXT,
            priority TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add latitude if the existing database doesn't have it
    try:
        cursor.execute(
            "ALTER TABLE incidents ADD COLUMN latitude REAL"
        )
    except sqlite3.OperationalError:
        pass

    # Add longitude if the existing database doesn't have it
    try:
        cursor.execute(
            "ALTER TABLE incidents ADD COLUMN longitude REAL"
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()