from users import UserManager, Role, User  # Import from the correct file 'users.py'
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Set up the database connection and session
engine = create_engine('sqlite:///faculty_on_site.db')  # Update with your database URI
Session = sessionmaker(bind=engine)

# Create a session instance
session = Session()

# Create a UserManager instance
user_manager = UserManager(session)  # Pass the session instance to UserManager

# Test: Create some test users
user_manager.create_user("alice", "password123", Role.STUDENT)
user_manager.create_user("bob", "password123", Role.FACULTY)
user_manager.create_user("admin", "admin123", Role.ADMIN)

# List users to verify
print("\nList of Users:")
user_manager.list_users()

# Authenticate a user (example: trying to authenticate 'alice')
user = user_manager.authenticate_user("alice", "password123")
if user:
    print(f"\nAuthenticated User: {user}")
else:
    print("\nAuthentication failed for 'alice'.")

# Retrieve a user by ID (example: retrieving user with ID 1)
user_by_id = user_manager.get_user_by_id(1)
if user_by_id:
    print(f"\nUser with ID 1: {user_by_id}")
else:
    print("\nUser not found with ID 1.")
