from dronekit import connect
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class VesselController:
    def __init__(self, role):
        self.role = role.upper()  # Convert role to uppercase for consistency
        
        # Get the connection string based on the role
        connection_string = self.get_connection_string()
        
        # Initialize the connection to the vehicle
        print(f"Connecting to vehicle on: {connection_string}")
        self.vehicle = connect(connection_string, wait_ready=True)
    
    def get_connection_string(self):
        connection_string = os.getenv(f'{self.role}_CONNECTION_STRING')
        if not connection_string:
            raise ValueError(f"Missing connection string for role: {self.role}")
        return connection_string
    
    # Function to retrieve telemetry data from the vehicle
    def get_telemetry(self):
        # Get the current timestamp in the format dd/mm/yyyy - HH:MM:SS
        timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        
        # Get current heading (yaw) in degrees from the vehicle
        heading = self.vehicle.heading
        
        # Get ground speed in meters per second and round to two decimal places
        ground_speed = round(self.vehicle.groundspeed, 2)
        
        # Get latitude and longitude from the vehicle's GPS location
        lat = self.vehicle.location.global_frame.lat
        lon = self.vehicle.location.global_frame.lon
        
        # Create a payload string for MQTT
        payload = f"Timestamp: {timestamp}, Heading: {heading} degrees, Ground Speed: {ground_speed} m/s, Latitude: {lat}, Longitude: {lon}"
        
        return payload
    
    # Function to close the vehicle connection
    def close_connection(self):
        self.vehicle.close()
        print("Vehicle connection closed.")
