from dronekit import connect
from datetime import datetime

class VesselController:
    def __init__(self, connection_string='udp:127.0.0.1:14550'):
        # Initialize the connection to the vehicle
        print(f"Connecting to vehicle on: {connection_string}")
        self.vehicle = connect(connection_string, wait_ready=True)
    
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
