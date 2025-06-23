import time
import os
from dotenv import load_dotenv
from mqtt_handler import MQTTHandler
from vessel_controller import VesselController

# Load environment variables from the .env file located one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    print("Starting scout vessel...")
    
    try:
        # Initialize MQTT handler and vessel controller for scout
        mqtt_handler = MQTTHandler('SCOUT')
        vessel_controller = VesselController('SCOUT')
        
        print("Scout vessel ready. Publishing telemetry...")
        
        # Main loop to get telemetry data and publish it every 5 seconds
        # Note: MQTT connection is maintained automatically by the background thread
        while True:
            try:
                # Get telemetry data from the vessel
                telemetry_data = vessel_controller.get_telemetry()
                
                # Publish telemetry data to the MQTT broker with QoS 0
                # Scout positions are frequent updates, QoS 0 is appropriate
                published_payload = mqtt_handler.publish(telemetry_data, qos=0)
                print(published_payload)
                
            except Exception as e:
                print(f"An error occurred in the main loop: {e}")
                # Try to reconnect on error
                try:
                    mqtt_handler.client.reconnect()
                except:
                    print("Reconnection failed, will retry next cycle")
                    time.sleep(5)
            
            # Wait for 5 seconds before the next data output
            time.sleep(5)
            
    except KeyboardInterrupt:
        # Catch keyboard interrupt (Ctrl+C) to exit the script gracefully
        print("\nShutting down scout vessel...")
        
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