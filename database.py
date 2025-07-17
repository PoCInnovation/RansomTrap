from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()
DB_PATH = os.getenv("DB_PATH")

def init_database():
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS Lures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            signature TEXT NOT NULL,
            path TEXT NOT NULL,
            path_copy TEXT NOT NULL
        );
        '''

        cursor.execute(create_table_query)
        connection.commit()

        print(f"✅ Table 'Lures' created successfully at {DB_PATH}!")

def insert_lure_in_db(filename, signature, path, path_copy):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Lures (filename, signature, path, path_copy) VALUES (?, ?, ?, ?);",
            (filename, signature, path, path_copy)
        )
        connection.commit()
        print(f"[➕] Lure inserted: {filename} at {path}\n")
