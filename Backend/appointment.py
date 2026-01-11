from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from users import UserManager


# Set up SQLAlchemy ORM
Base = declarative_base()

# Define Appointment class for database interaction
class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    faculty_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date_time = Column(DateTime, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)

    student = relationship("User", foreign_keys=[student_id])
    faculty = relationship("User", foreign_keys=[faculty_id])

    def __repr__(self):
        """Return a string representation of the appointment."""
        return f"Appointment(ID: {self.id}, Student: {self.student.username}, Faculty: {self.faculty.username}, Time: {self.date_time}, Status: {self.status})"


class AppointmentManager:
    def __init__(self, user_manager, db_url='ssqlite:///faculty_on_site.db'):
        """Initialize the AppointmentManager with a user manager and database connection."""
        self.db_url = db_url
        self.engine = create_engine(self.db_url, echo=True)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)
        self.user_manager = user_manager

    def request_appointment(self, student_id, faculty_id, date_time, reason):
        """Create a new appointment request."""
        session = self.Session()
        student = self.user_manager.get_user_by_id(student_id)
        faculty = self.user_manager.get_user_by_id(faculty_id)

        if not student or not faculty:
            print("Invalid student or faculty ID!")
            session.close()
            return None

        if not self.is_slot_available(date_time):
            print(f"Time slot {date_time} is already booked!")
            session.close()
            return None

        # Create and add the new appointment to the database
        appointment = Appointment(student_id=student.id, faculty_id=faculty.id, date_time=date_time, reason=reason)
        session.add(appointment)
        session.commit()
        session.close()
        print(f"Appointment requested by Student {student.username} with Faculty {faculty.username} at {date_time}.")
        return appointment

    def accept_appointment(self, appointment_id):
        """Accept an appointment request."""
        session = self.Session()
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()
        if appointment and appointment.status == "pending":
            appointment.status = "accepted"
            session.commit()
            session.close()
            print(f"Appointment {appointment_id} has been accepted.")
        else:
            session.close()
            print(f"Appointment {appointment_id} cannot be accepted.")

    def reject_appointment(self, appointment_id):
        """Reject an appointment request."""
        session = self.Session()
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()
        if appointment and appointment.status == "pending":
            appointment.status = "rejected"
            session.commit()
            session.close()
            print(f"Appointment {appointment_id} has been rejected.")
        else:
            session.close()
            print(f"Appointment {appointment_id} cannot be rejected.")

    def is_slot_available(self, date_time):
        """Check if the requested time slot is already taken."""
        session = self.Session()
        existing_appointment = session.query(Appointment).filter_by(date_time=date_time, status="accepted").first()
        session.close()
        return existing_appointment is None

    def get_appointment_by_id(self, appointment_id):
        """Retrieve an appointment by its ID."""
        session = self.Session()
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()
        session.close()
        return appointment

    def list_appointments(self):
        """List all appointments."""
        session = self.Session()
        appointments = session.query(Appointment).all()
        session.close()
        for appointment in appointments:
            print(appointment)

    def edit_appointment(self, user_id, appointment_id, new_date_time=None, new_reason=None):
        """Edit an appointment, only allowed for administrators."""
        user = self.user_manager.get_user_by_id(user_id)
        if not user or user.role != 'administrator':
            print("Only administrators can edit appointments.")
            return

        session = self.Session()
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()
        if appointment:
            if new_date_time:
                if self.is_slot_available(new_date_time):
                    appointment.date_time = new_date_time
                    print(f"Appointment {appointment_id} date and time updated to {new_date_time}.")
                else:
                    print(f"Time slot {new_date_time} is already booked!")
            if new_reason:
                appointment.reason = new_reason
                print(f"Appointment {appointment_id} reason updated.")
            session.commit()
        else:
            print(f"Appointment {appointment_id} not found.")
        session.close()
