import sqlite3

def create_db():
    # Connect to SQLite3 Database (or create it)
    conn = sqlite3.connect('faculty_on_site.db')
    cursor = conn.cursor()

    # Create tables for users, appointments, and cancellation requests
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'faculty', 'admin'))
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        faculty_id INTEGER NOT NULL,
        date_time TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')) NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cancellation_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL,
        requester_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')) NOT NULL
    )''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

create_db()
