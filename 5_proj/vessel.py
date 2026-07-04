import time
import argparse
import os
from dotenv import load_dotenv
from mqtt_handler import MQTTHandler
from vessel_controller import VesselController

# Load environment variables from the .env file located one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Follower vessel telemetry system with scout subscription')
    parser.add_argument('role', choices=['vessel1', 'vessel2', 'vessel3'],
                       help='Vessel role (vessel1, vessel2, or vessel3)')

    # Parse command-line arguments
    args = parser.parse_args()
    role = args.role

    print(f"Starting {role} vessel...")

    try:
        # Initialize MQTT handler and vessel controller for the specified role
        mqtt_handler = MQTTHandler(role)
        vessel_controller = VesselController(role)
        
        # Subscribe to scout position topic
        mqtt_handler.subscribe('SCOUT_POSITION_TOPIC')
        
        # Main loop to get telemetry data and publish it every 5 seconds
        while True:
            # Get telemetry data from the vessel
            telemetry_data = vessel_controller.get_telemetry()
            
            # Publish telemetry data to the MQTT broker and get the actual payload sent
            published_payload = mqtt_handler.publish(telemetry_data)
            print(published_payload)
            
            # Wait for 5 seconds before the next data output
            time.sleep(5)
            
    except KeyboardInterrupt:
        # Catch keyboard interrupt (Ctrl+C) to exit the script gracefully
        print("Exiting script...")
        
    except Exception as e:
        # Catch any other errors (missing environment variables, connection failures, etc.)
        print(f"Error: {e}")
        
    finally:
        # Ensure both MQTT and vehicle connections are closed before exiting
        try:
            vessel_controller.close_connection()
            mqtt_handler.disconnect()
        except:
            pass  # Ignore errors during cleanup
        print("All connections closed. Exiting.")

if __name__ == "__main__":
    main()