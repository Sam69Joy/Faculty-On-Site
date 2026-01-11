from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from users import UserManager  # Import UserManager class from user.py
from appointment import AppointmentManager  # Import AppointmentManager class from appointment.py
from enum import Enum as PyEnum

Base = declarative_base()

class CancellationRequestStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class CancellationRequest(Base):
    __tablename__ = 'cancellation_requests'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    requester_id = Column(Integer, ForeignKey('users.id'))
    reason = Column(String)
    status = Column(Enum(CancellationRequestStatus), default=CancellationRequestStatus.PENDING)
    
    # Relationships
    appointment = relationship("Appointment", backref="cancellation_requests")
    requester = relationship("User", backref="cancellation_requests")
    
    def __str__(self):
        """String representation of the cancellation request."""
        return f"CancellationRequest(ID: {self.appointment_id}, Requester: {self.requester.username}, Reason: {self.reason}, Status: {self.status.value})"


class CancellationManager:
    def __init__(self, appointment_manager, user_manager, db_url='sqlite:///faculty_on_site.db'):
        """Initialize the cancellation manager with appointment and user managers."""
        self.db_url = db_url
        self.engine = create_engine(self.db_url, echo=True)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)
        self.appointment_manager = appointment_manager
        self.user_manager = user_manager

    def request_cancellation(self, appointment_id, requester_id, reason):
        """Request a cancellation of an appointment."""
        session = self.Session()
        
        # Check if the appointment exists
        appointment = self.appointment_manager.get_appointment_by_id(appointment_id)
        if not appointment:
            print("Appointment not found!")
            return

        # Check if the requester is a student or faculty member
        requester = self.user_manager.get_user_by_id(requester_id)
        if not requester:
            print("Invalid user!")
            return

        if requester.role not in ['student', 'faculty']:
            print("Only students or faculty members can request cancellation.")
            return
        
        # Create a cancellation request and add it to the database
        cancellation_request = CancellationRequest(
            appointment_id=appointment_id,
            requester_id=requester_id,
            reason=reason
        )
        session.add(cancellation_request)
        session.commit()
        print(f"Cancellation request from {requester.username} for Appointment {appointment_id} has been created.")
        session.close()

    def admin_accept_or_reject(self, appointment_id, admin_id, action, reason=None):
        """Admin can accept or reject the cancellation request."""
        session = self.Session()

        # Check if the user is an administrator
        admin = self.user_manager.get_user_by_id(admin_id)
        if admin and admin.role != 'administrator':
            print("Only administrators can accept or reject cancellation requests.")
            session.close()
            return

        # Find the cancellation request
        cancellation_request = session.query(CancellationRequest).filter(CancellationRequest.appointment_id == appointment_id).first()
        if not cancellation_request:
            print("Cancellation request not found!")
            session.close()
            return
        
        # Admin action: accept or reject the cancellation
        if action == 'accept':
            cancellation_request.status = CancellationRequestStatus.ACCEPTED
            print(f"Admin {admin.username} accepted the cancellation request for Appointment {appointment_id}.")
            # Change the appointment status to canceled (this can also be done in the appointment manager)
            self.appointment_manager.cancel_appointment(appointment_id)
        elif action == 'reject':
            cancellation_request.status = CancellationRequestStatus.REJECTED
            print(f"Admin {admin.username} rejected the cancellation request for Appointment {appointment_id}.")
        else:
            print("Invalid action. Use 'accept' or 'reject'.")
        
        session.commit()
        session.close()

    def list_cancellation_requests(self):
        """List all cancellation requests."""
        session = self.Session()
        requests = session.query(CancellationRequest).all()
        for request in requests:
            print(request)
        session.close()
