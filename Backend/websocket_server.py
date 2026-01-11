import asyncio
import websockets
import json
from appointment import AppointmentManager
from users import UserManager
from cancellation import CancellationManager

# Create instances of UserManager, AppointmentManager, and CancellationManager
user_manager = UserManager()
appointment_manager = AppointmentManager(user_manager)
cancellation_manager = CancellationManager(appointment_manager, user_manager)

# WebSocket server to handle real-time updates
async def handle_client(websocket, path):
    """Handles communication with the client."""
    # Register the client for broadcasting updates
    connected_clients.add(websocket)
    
    try:
        while True:
            message = await websocket.recv()  # Receive a message from the client
            data = json.loads(message)
            
            # Handle actions based on the message received
            if data.get("action") == "request_appointment":
                student_id = data.get("student_id")
                faculty_id = data.get("faculty_id")
                date_time = data.get("date_time")
                reason = data.get("reason")
                appointment = appointment_manager.request_appointment(student_id, faculty_id, date_time, reason)
                if appointment:
                    # Broadcast the new appointment to all connected clients
                    await broadcast_appointment_update(appointment)

            elif data.get("action") == "request_cancellation":
                appointment_id = data.get("appointment_id")
                requester_id = data.get("requester_id")
                reason = data.get("reason")
                cancellation_manager.request_cancellation(appointment_id, requester_id, reason)
                # Broadcast cancellation request
                await broadcast_cancellation_update(appointment_id)

            elif data.get("action") == "admin_accept_cancellation":
                appointment_id = data.get("appointment_id")
                admin_id = data.get("admin_id")
                cancellation_manager.admin_accept_or_reject(appointment_id, admin_id, "accept")
                await broadcast_cancellation_update(appointment_id)

            elif data.get("action") == "admin_reject_cancellation":
                appointment_id = data.get("appointment_id")
                admin_id = data.get("admin_id")
                cancellation_manager.admin_accept_or_reject(appointment_id, admin_id, "reject")
                await broadcast_cancellation_update(appointment_id)

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        # Unregister the client when they disconnect
        connected_clients.remove(websocket)

# Broadcast updates to all clients
async def broadcast_appointment_update(appointment):
    """Broadcast updated appointment to all connected clients."""
    message = json.dumps({
        "action": "update_appointment",
        "appointment": str(appointment)
    })
    await send_to_all_clients(message)

async def broadcast_cancellation_update(appointment_id):
    """Broadcast cancellation request update to all connected clients."""
    message = json.dumps({
        "action": "update_cancellation",
        "appointment_id": appointment_id
    })
    await send_to_all_clients(message)

# Function to send messages to all connected clients
connected_clients = set()

async def send_to_all_clients(message):
    """Send the message to all connected WebSocket clients."""
    for client in connected_clients:
        await client.send(message)

# Start WebSocket server
async def start_server():
    """Start the WebSocket server to listen for connections."""
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # Run server until interrupted

if __name__ == "__main__":
    print("WebSocket server is running on ws://localhost:8765")
    asyncio.run(start_server())
