import paho.mqtt.client as mqtt
import os
import ssl
from dotenv import load_dotenv
import json

# Load environment variables from the .env file located one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class MQTTHandler:
    def __init__(self, role):
        self.role = role.upper()  # Convert to uppercase for consistency
        
        # Initialize MQTT connection details from role-specific environment variables
        self.broker = os.getenv('MQTT_BROKER')
        self.port = int(os.getenv('MQTT_PORT'))
        self.username = os.getenv(f'{self.role}_MQTT_USERNAME')
        self.password = os.getenv(f'{self.role}_MQTT_PASSWORD')
        self.topic = os.getenv(f'{self.role}_POSITION_TOPIC')
        self.use_tls = os.getenv('MQTT_USE_TLS', 'false').lower() == 'true'
        
        # Validate all required configuration is present
        if not all([self.broker, self.port, self.username, self.password, self.topic]):
            raise ValueError(f"Missing required MQTT configuration for role: {self.role}")
        
        # Initialize MQTT client and set up connection
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(self.username, self.password)
        
        # Configure TLS if enabled in environment variables
        if self.use_tls:
            # Create an SSLContext that loads system CAs (which include Let's Encrypt)
            ctx = ssl.create_default_context()
            self.client.tls_set_context(ctx)
            print("TLS enabled, using system default CA certificates")
        else:
            print("TLS disabled, using non-secure connection")
        
        # Attempt to connect to MQTT broker with error handling
        try:
            print(f"Connecting to {self.broker}:{self.port} ...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print("Successfully connected to MQTT broker")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            raise
    
    # Function to publish a message to the MQTT broker
    def publish(self, payload):
        # Add the boat identifier to the payload
        payload['boat'] = self.username
        
        # Convert the payload to a JSON string
        json_payload = json.dumps(payload)
        
        # Publish the JSON payload to the MQTT broker
        result = self.client.publish(self.topic, json_payload)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Successfully published to MQTT topic: {self.topic}")
        else:
            print(f"Failed to publish to MQTT: {result.rc}")
        
        # Return the actual payload that was sent
        return json_payload
    
    def subscribe(self, topic_names):
        # Handle single topic or list of topics
        if isinstance(topic_names, str):
            topic_names = [topic_names]
            
        for topic_name in topic_names:
            topic = os.getenv(topic_name)
            if not topic:
                raise ValueError(f"Missing {topic_name} in environment variables")
            
            self.client.subscribe(topic)
            self.client.message_callback_add(topic, self.on_message)
            print(f"Subscribed to topic: {topic}")
    
    def on_message(self, client, userdata, msg):
        # First, try to parse the message as JSON
        try:
            payload = json.loads(msg.payload.decode())
            print(f"Received message on topic {msg.topic}:")
            
            if 'latitude' in payload and 'longitude' in payload:
                print(f"  Latitude: {payload['latitude']}, Longitude: {payload['longitude']}")
            elif msg.topic.lower().endswith('commands'):
                command = payload.get('command', '').lower()
                self.handle_command(command)
            else:
                print(f"  Payload: {payload}")
                
        except json.JSONDecodeError:
            # If JSON parsing fails, treat it as plain text command if from command topic
            if msg.topic.lower().endswith('commands'):
                command = msg.payload.decode().strip().lower()
                self.handle_command(command)
            else:
                print(f"Received invalid JSON message on topic {msg.topic}: {msg.payload.decode()}")
    
    def handle_command(self, command):
        if command == "follow":
            self.print_command_message("Command to start following is issued")
        elif command == "stop":
            self.print_command_message("Command to stop following is issued")
        else:
            self.print_command_message(f"Unknown command received: {command}")
    
    def print_command_message(self, message):
        print("\n" + "*" * 50)
        print(message)
        print("*" * 50 + "\n")
    
    # Function to disconnect the MQTT client
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()