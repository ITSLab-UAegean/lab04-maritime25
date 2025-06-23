from dronekit import connect, VehicleMode
import time
from datetime import datetime

# Connect to the vehicle (SITL) using the specified connection string
connection_string = 'udp:127.0.0.1:14550'
print(f"Connecting to vehicle on: {connection_string}")

# Establish a connection to the vehicle
# 'wait_ready=True' ensures the script waits until all vehicle parameters are loaded
vehicle = connect(connection_string, wait_ready=True)

# Function to output basic telemetry data
def get_telemetry():
    # Get the current timestamp
    timestamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
    
    # Get current heading (yaw) in degrees from the vehicle
    heading = vehicle.heading
    
    # Get ground speed in meters per second and round to two decimal places
    ground_speed = round(vehicle.groundspeed, 2)
    
    # Get latitude and longitude from the vehicle's GPS location
    lat = vehicle.location.global_frame.lat
    lon = vehicle.location.global_frame.lon
    
    # Print the telemetry data to the console
    print(f"Timestamp: {timestamp}")
    print(f"Heading: {heading} degrees")
    print(f"Ground Speed: {ground_speed} m/s")
    print(f"Latitude: {lat}")
    print(f"Longitude: {lon}")
    print('-' * 30)

try:
    # Main loop to continuously read and print telemetry data every 5 seconds
    while True:
        get_telemetry()  # Call the function to print telemetry data
        time.sleep(5)    # Wait for 5 seconds before the next update
        
except KeyboardInterrupt:
    # Catch keyboard interrupt (Ctrl+C) to exit gracefully
    print("Exiting script...")
    
finally:
    # Ensure the vehicle connection is closed before exiting
    vehicle.close()
    print("Vehicle connection closed.")