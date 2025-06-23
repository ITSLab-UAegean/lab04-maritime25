from dronekit import connect
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import ssl

# Load environment variables from the .env file located one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# MQTT connection details from environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_USE_TLS = os.getenv('MQTT_USE_TLS', 'false').lower() == 'true'
MQTT_TOPIC = 'leader/position'  # Hardcoded topic for this project

# Connect to the vehicle (SITL) using the specified connection string
connection_string = 'udp:127.0.0.1:14550'
print(f"Connecting to vehicle on: {connection_string}")

# Establish a connection to the vehicle
vehicle = connect(connection_string, wait_ready=True)

# Function to publish telemetry data to MQTT broker
def publish_to_mqtt(client, payload):
    # Publish the payload to the specified MQTT topic
    result = client.publish(MQTT_TOPIC, payload)
    
    # Check the result of the publish operation
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Successfully published to MQTT.")
    else:
        print(f"Failed to publish to MQTT: {result.rc}")

# Function to output basic telemetry data
def get_telemetry():
    # Get the current timestamp in the format dd/mm/yyyy - HH:MM:SS
    timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    
    # Get current heading (yaw) in degrees from the vehicle
    heading = vehicle.heading
    
    # Get ground speed in meters per second and round to two decimal places
    ground_speed = round(vehicle.groundspeed, 2)
    
    # Get latitude and longitude from the vehicle's GPS location
    lat = vehicle.location.global_frame.lat
    lon = vehicle.location.global_frame.lon
    
    # Create a payload string for MQTT
    payload = f"Timestamp: {timestamp}, Heading: {heading} degrees, Ground Speed: {ground_speed} m/s, Latitude: {lat}, Longitude: {lon}"
    
    # Print the telemetry data to the console
    print(payload)
    
    # Publish the telemetry data to the MQTT broker
    publish_to_mqtt(client, payload)

# Initialize MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # Use VERSION2 to suppress deprecation warning
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Configure TLS if enabled in environment variables
if MQTT_USE_TLS:
    # Create an SSLContext that loads system CAs (which include Let's Encrypt)
    ctx = ssl.create_default_context()
    client.tls_set_context(ctx)
    print("TLS enabled, using system default CA certificates")
else:
    print("TLS disabled, using non-secure connection")

print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT} ...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Start the loop in a separate thread

try:
    # Main loop to continuously read and publish telemetry data every 5 seconds
    while True:
        get_telemetry()  # Call the function to get and publish telemetry data
        time.sleep(5)    # Wait for 5 seconds before the next data output
        
except KeyboardInterrupt:
    # Catch keyboard interrupt (Ctrl+C) to exit the script gracefully
    print("Exiting script...")
    
finally:
    # Ensure the vehicle connection is closed and MQTT loop is stopped
    vehicle.close()
    client.loop_stop()
    client.disconnect()
    print("Vehicle connection closed and MQTT client disconnected.")