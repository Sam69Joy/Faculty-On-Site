from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt
from enum import Enum as PyEnum

Base = declarative_base()

# Define user roles as an Enum for SQLAlchemy compatibility
class Role(PyEnum):
    STUDENT = 'student'
    FACULTY = 'faculty'
    ADMIN = 'administrator'

# User class to handle user data
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)  # Use Enum from SQLAlchemy

    def __init__(self, username, password, role):
        """Initialize user with username, password (hashed), and role."""
        self.username = username
        self.password = password  # This will be the hashed password
        self.role = role  # Can be 'student', 'faculty', or 'administrator'

    def __str__(self):
        """Return a string representation of the user."""
        return f"User(ID: {self.id}, Username: {self.username}, Role: {self.role})"

# UserManager class to handle user management, creation, and authentication
class UserManager:
    def __init__(self, session):
        """Initialize the UserManager with a SQLAlchemy session."""
        self.session = session

    def create_user(self, username, password, role):
        """Create a new user with hashed password and add it to the database."""
        hashed_password = self.hash_password(password)
        new_user = User(username=username, password=hashed_password, role=role)
        self.session.add(new_user)
        self.session.commit()
        print(f"User {username} created successfully.")

    def hash_password(self, password):
        """Hash the password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    def verify_password(self, hashed_password, password):
        """Verify if the password matches the hashed password."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def authenticate_user(self, username, password):
        """Authenticate a user by matching username and verifying password."""
        user = self.session.query(User).filter(User.username == username).first()
        if user and self.verify_password(user.password, password):
            return user
        return None  # If no user matches

    def list_users(self):
        """List all users."""
        users = self.session.query(User).all()
        for user in users:
            print(user)

    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID."""
        user = self.session.query(User).get(user_id)
        return user
