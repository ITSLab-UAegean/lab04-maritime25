from dronekit import connect, VehicleMode, LocationGlobalRelative
from datetime import datetime
import os
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2
import time
from collections import deque

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Station angle for each vessel, in degrees relative to the scout's heading:
# where the vessel sits in the formation. 0 would be dead ahead of the scout,
# +135 is behind and to the right (starboard quarter), -135 behind and to the
# left (port quarter), 180 directly astern. Because the angles are relative
# to the heading, the formation rotates with the scout and stays "behind" it
# whichever way it turns.
FORMATION_ANGLES = {
    'VESSEL1': -135,   # port quarter
    'VESSEL2': 135,    # starboard quarter
    'VESSEL3': 180,    # directly astern
}

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

        # Safe follow distance in meters (set in .env): closer to the scout
        # than this, the vessel loiters instead of pressing on
        self.safe_follow_distance = float(os.getenv('SAFE_FOLLOW_DISTANCE', 5))

        # Formation station (set in .env): how far from the scout this vessel
        # stations, at its angle from the table above
        self.formation_distance = float(os.getenv('FORMATION_DISTANCE', 30))
        self.station_angle = FORMATION_ANGLES.get(self.role, 180)

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

    def offset_position(self, lat, lon, bearing_deg, distance_m):
        # The point distance_m meters away from (lat, lon) along a compass
        # bearing. Flat-earth approximation: one degree of latitude is about
        # 111320 m, one degree of longitude shrinks with cos(latitude).
        # Plenty accurate at formation distances (tens of meters).
        bearing = radians(bearing_deg)
        dlat = distance_m * cos(bearing) / 111320
        dlon = distance_m * sin(bearing) / (111320 * cos(radians(lat)))
        return lat + dlat, lon + dlon

    def report_status(self, distance):
        current_time = time.time()
        if current_time - self.last_report_time >= self.report_interval:
            mode = "LOITERING" if self.following and distance < self.safe_follow_distance else \
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

    def follow_scout(self, scout_lat, scout_lon, scout_speed, scout_heading):
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
            if current_distance < self.safe_follow_distance:
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
                    # Aim for this vessel's formation station, not the scout
                    # itself: the point formation_distance meters from the
                    # scout, at station_angle relative to the scout's heading
                    station_lat, station_lon = self.offset_position(
                        scout_lat, scout_lon,
                        scout_heading + self.station_angle,
                        self.formation_distance
                    )
                    print(f"Issuing new goto command. Distance to scout: {current_distance:.2f} meters")
                    self.vehicle.simple_goto(LocationGlobalRelative(station_lat, station_lon, 0))
                    self.last_goto_time = current_time
                    # Keep tracking the SCOUT's position here (scout_has_moved
                    # compares against it), even though the goto targets the station
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
