import time
from mqtt_handler import MQTTHandler
from vessel_controller import VesselController

def main():
    # Initialize MQTT handler and vessel controller
    mqtt_handler = MQTTHandler()
    vessel_controller = VesselController()
    
    try:
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
        
    finally:
        # Ensure both MQTT and vehicle connections are closed before exiting
        vessel_controller.close_connection()
        mqtt_handler.disconnect()
        print("All connections closed. Exiting.")

# Run the main function if this script is executed
if __name__ == "__main__":
    main()