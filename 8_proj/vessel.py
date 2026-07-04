import time
import argparse
import os
from dotenv import load_dotenv
from mqtt_handler import MQTTHandler
from vessel_controller import VesselController
import json

# Load environment variables from the .env file located one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def on_message(client, userdata, msg):
    vessel_controller = userdata['vessel_controller']

    try:
        payload = json.loads(msg.payload.decode())

        # Handle scout position updates (heading included: the formation
        # stations are computed relative to the scout's heading)
        if all(key in payload for key in ('latitude', 'longitude', 'ground_speed', 'heading')):
            if vessel_controller.following:
                vessel_controller.follow_scout(
                    payload['latitude'],
                    payload['longitude'],
                    payload['ground_speed'],
                    payload['heading']
                )
        # Handle commands
        elif msg.topic.lower().endswith('commands'):
            command = payload.get('command', '').lower()
            handle_command(command, vessel_controller)

    except json.JSONDecodeError:
        # Handle plaintext commands
        if msg.topic.lower().endswith('commands'):
            command = msg.payload.decode().strip().lower()
            handle_command(command, vessel_controller)
        else:
            print(f"Received invalid message on topic {msg.topic}: {msg.payload.decode()}")

    except Exception as e:
        print(f"Error processing message: {e}")

def handle_command(command, vessel_controller):
    if command == "follow":
        print("\n" + "*" * 50)
        print("Command to start following is issued")
        print("*" * 50 + "\n")
        vessel_controller.arm_vehicle()
        vessel_controller.set_guided_mode()

    elif command == "stop":
        print("\n" + "*" * 50)
        print("Command to stop following is issued")
        print("*" * 50 + "\n")
        vessel_controller.stop_following()
    else:
        print(f"Unknown command received: {command}")

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Follower vessel with formation-keeping follow behavior')
    parser.add_argument('role', choices=['vessel1', 'vessel2', 'vessel3'],
                       help='Vessel role (vessel1, vessel2, or vessel3)')

    # Parse command-line arguments
    args = parser.parse_args()
    role = args.role

    print(f"Starting {role} vessel...")

    # Telemetry publish rate in seconds, set in .env (no longer hardcoded:
    # the whole fleet's update rate is now tunable in one place)
    telemetry_interval = float(os.getenv('TELEMETRY_INTERVAL', 5))

    try:
        # Initialize MQTT handler and vessel controller for the specified role
        vessel_controller = VesselController(role)
        mqtt_handler = MQTTHandler(role)

        # Create a list of topics to subscribe to
        topics_to_subscribe = ['SCOUT_POSITION_TOPIC', f'{role.upper()}_COMMANDS']

        # Set vessel controller in userdata for callback access
        mqtt_handler.client.user_data_set({'vessel_controller': vessel_controller})

        # Subscribe to topics with custom callback
        # QoS will be automatically set to 1 for commands, 0 for positions
        mqtt_handler.subscribe(topics_to_subscribe, on_message)

        print("Vessel ready. Waiting for commands...")

        # Main loop to get telemetry data and publish it every TELEMETRY_INTERVAL seconds
        # Note: MQTT messages are processed automatically by the background thread
        while True:
            try:
                # Get telemetry data from the vessel
                telemetry_data = vessel_controller.get_telemetry()

                # Publish telemetry data to the MQTT broker with QoS 0
                published_payload = mqtt_handler.publish(telemetry_data, qos=0)
                print(published_payload)

            except Exception as e:
                print(f"An error occurred in the main loop: {e}")

            # Wait before the next telemetry output
            time.sleep(telemetry_interval)

    except KeyboardInterrupt:
        # Catch keyboard interrupt (Ctrl+C) to exit the script gracefully
        print("\nShutting down vessel...")

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
