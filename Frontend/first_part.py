# frontend_view.py
import sys
import os

from Backend import websocket_server

import tkinter as tk
import customtkinter as ctk
import websockets
import asyncio
import json
import threading

# Global variables to store real-time data
appointments = []
cancellations = []

class RealTimeUpdateApp:
    def __init__(self, root):
        """Initialize the Tkinter window and connect to WebSocket server."""
        self.root = root
        self.root.title("Real-Time Appointment and Cancellation View")

        # Set up Tkinter widgets for displaying appointment and cancellation status
        self.appointment_listbox = ctk.CTkListbox(self.root, height=10, width=50)
        self.appointment_listbox.pack(pady=10)

        self.cancellation_listbox = ctk.CTkListbox(self.root, height=10, width=50)
        self.cancellation_listbox.pack(pady=10)

        # Start the WebSocket listener in a separate thread
        threading.Thread(target=self.start_websocket_listener, daemon=True).start()

    async def websocket_listener(self):
        """Listen for WebSocket messages and update the UI accordingly."""
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                if data.get("action") == "update_appointment":
                    appointment = data.get("appointment")
                    appointments.append(appointment)
                    self.update_appointment_list()

                elif data.get("action") == "update_cancellation":
                    appointment_id = data.get("appointment_id")
                    cancellations.append(appointment_id)
                    self.update_cancellation_list()

    def start_websocket_listener(self):
        """Start the WebSocket listener in the background."""
        asyncio.run(self.websocket_listener())

    def update_appointment_list(self):
        """Update the appointment list in the UI."""
        self.appointment_listbox.delete(0, ctk.END)
        for appointment in appointments:
            self.appointment_listbox.insert(ctk.END, appointment)

    def update_cancellation_list(self):
        """Update the cancellation list in the UI."""
        self.cancellation_listbox.delete(0, ctk.END)
        for appointment_id in cancellations:
            self.cancellation_listbox.insert(ctk.END, f"Cancellation request for Appointment {appointment_id}")

# Create the main Tkinter window
root = ctk.CTk()

# Initialize and run the real-time update application
app = RealTimeUpdateApp(root)
root.mainloop()
