from dronekit import connect, VehicleMode, LocationGlobalRelative
from datetime import datetime
import os
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2
import time
from collections import deque

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class VesselController:
    def __init__(self, role):
        self.role = role.upper()  # Convert role to uppercase for consistency
        self.following = False
        self.last_scout_distance = None
        self.last_goto_time = time.time()
        self.last_goto_position = None
        self.last_report_time = 0
        self.report_interval = 3  # Report every 3 seconds
        self.scout_speeds = deque(maxlen=3)  # Store last 3 speed readings
        
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
        
        # Create a dictionary with telemetry data
        telemetry_data = {
            "timestamp": timestamp,
            "heading": self.vehicle.heading,
            "ground_speed": round(self.vehicle.groundspeed, 2),
            "latitude": self.vehicle.location.global_frame.lat,
            "longitude": self.vehicle.location.global_frame.lon
        }
        
        return telemetry_data
    
    def arm_vehicle(self):
        # Arm the vehicle if it's not already armed
        if not self.vehicle.armed:
            print("Arming vehicle...")
            self.vehicle.armed = True
            while not self.vehicle.armed:
                time.sleep(1)
            print("Vehicle armed.")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Calculate the great circle distance between two points on earth
        R = 6371000  # Earth radius in meters
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def report_status(self, distance):
        current_time = time.time()
        if current_time - self.last_report_time >= self.report_interval:
            mode = "LOITERING" if self.following and distance < 5 else \
                   "STOPPED" if not self.following else "FOLLOWING"
            print(f"Distance to scout: {distance:.2f} meters. Mode: {mode}")
            self.last_report_time = current_time
    
    def scout_has_moved(self, scout_lat, scout_lon, scout_speed):
        if self.last_goto_position is None:
            return True
        
        distance_moved = self.calculate_distance(
            self.last_goto_position[0], self.last_goto_position[1],
            scout_lat, scout_lon
        )
        
        self.scout_speeds.append(scout_speed)
        avg_speed = sum(self.scout_speeds) / len(self.scout_speeds)
        
        # Consider scout moved if position changed >4m OR average speed >0.5 m/s
        return distance_moved > 4 or avg_speed > 0.5
    
    def follow_scout(self, scout_lat, scout_lon, scout_speed):
        current_time = time.time()
        
        # Calculate distance to scout
        current_distance = self.calculate_distance(
            self.vehicle.location.global_frame.lat,
            self.vehicle.location.global_frame.lon,
            scout_lat, scout_lon
        )
        
        self.report_status(current_distance)
        
        if self.following:
            # Check if too close to scout
            if current_distance < 5:
                if self.vehicle.mode.name != "LOITER":
                    self.vehicle.mode = VehicleMode("LOITER")
                    print("Too close to scout. Loitering to maintain position.")
            else:
                # Resume following if needed
                if self.vehicle.mode.name != "GUIDED":
                    self.vehicle.mode = VehicleMode("GUIDED")
                    print("Resuming follow mode.")
                
                # Determine if we should issue a new goto command
                should_update = (
                    self.last_goto_position is None or
                    current_time - self.last_goto_time >= 15 or
                    current_distance > self.last_scout_distance + 5
                )
                
                if should_update and self.scout_has_moved(scout_lat, scout_lon, scout_speed):
                    print(f"Issuing new goto command. Distance to scout: {current_distance:.2f} meters")
                    self.vehicle.simple_goto(LocationGlobalRelative(scout_lat, scout_lon, 0))
                    self.last_goto_time = current_time
                    self.last_goto_position = (scout_lat, scout_lon)
                    self.last_scout_distance = current_distance
    
    def set_guided_mode(self):
        # Set the vehicle mode to GUIDED and initialize following state
        self.vehicle.mode = VehicleMode("GUIDED")
        while self.vehicle.mode.name != "GUIDED":
            time.sleep(1)
        print("Vehicle is in GUIDED mode. Started following.")
        self.following = True
    
    def stop_following(self):
        # Stop following by switching to LOITER mode
        self.vehicle.mode = VehicleMode("LOITER")
        while self.vehicle.mode.name != "LOITER":
            time.sleep(1)
        print("Vehicle is in LOITER mode. Stopped following.")
        self.following = False
        self.last_scout_distance = None
        self.last_goto_time = None
        self.last_goto_position = None
        self.scout_speeds.clear()
    
    # Function to close the vehicle connection
    def close_connection(self):
        self.vehicle.close()
        print("Vehicle connection closed.")