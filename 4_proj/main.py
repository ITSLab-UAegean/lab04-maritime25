import time
import argparse
from mqtt_handler import MQTTHandler
from vessel_controller import VesselController

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Multi-vessel telemetry system')
    parser.add_argument('role', choices=['scout', 'team1', 'team2', 'team3'], 
                       help='Vessel role (scout, team1, team2, or team3)')
    
    # Parse command-line arguments
    args = parser.parse_args()
    role = args.role
    
    print(f"Starting {role} vessel...")
    
    try:
        # Initialize MQTT handler and vessel controller with the specified role
        mqtt_handler = MQTTHandler(role)
        vessel_controller = VesselController(role)
        
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

# Run the main function if this script is executed
if __name__ == "__main__":
    main()