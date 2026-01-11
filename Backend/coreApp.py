import sqlite3

class CoreApp:
    def __init__(self):
        self.db_name = 'faculty_on_site.db'

    def _connect(self):
        """Connect to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def get_user_by_id(self, user_id):
        """Fetch a user by their ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_user_by_username(self, username):
        """Fetch a user by their username."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    def create_user(self, username, password, role):
        """Create a new user with role check."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                       (username, password, role))
        conn.commit()
        conn.close()

    def update_user_role(self, user_id, new_role, admin_id):
        """Allow only admin to update user roles."""
        admin = self.get_user_by_id(admin_id)
        if admin and admin[3] == 'admin':  # Check if user is admin
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
            conn.commit()
            conn.close()
            print(f"User with ID {user_id} role updated to {new_role}.")
        else:
            print("Only admin can update user roles.")

    def create_appointment(self, student_id, faculty_id, date_time, reason):
        """Create a new appointment."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO appointments (student_id, faculty_id, date_time, reason, status) VALUES (?, ?, ?, ?, ?)', 
                       (student_id, faculty_id, date_time, reason, 'pending'))
        conn.commit()
        conn.close()

    def update_appointment_status(self, appointment_id, status, admin_id):
        """Allow only admin to update appointment status."""
        admin = self.get_user_by_id(admin_id)
        if admin and admin[3] == 'admin':  # Check if user is admin
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute('UPDATE appointments SET status = ? WHERE id = ?', (status, appointment_id))
            conn.commit()
            conn.close()
            print(f"Appointment with ID {appointment_id} status updated to {status}.")
        else:
            print("Only admin can update appointment status.")

    def cancel_appointment(self, appointment_id, admin_id):
        """Allow only admin to cancel appointments."""
        admin = self.get_user_by_id(admin_id)
        if admin and admin[3] == 'admin':  # Check if user is admin
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
            conn.commit()
            conn.close()
            print(f"Appointment with ID {appointment_id} has been canceled.")
        else:
            print("Only admin can cancel appointments.")
