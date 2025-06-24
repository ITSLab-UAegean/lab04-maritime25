# Project 3: Modular Architecture

**Learning Objective**: Refactor MQTT telemetry publishing into a modular, object-oriented architecture

## Key Concepts

This project maintains the same functionality as Project 2 but introduces a professional modular design pattern.

### Modular Design Pattern

The monolithic script from Project 2 is now split into three focused modules:

- **`mqtt_handler.py`**: Handles all MQTT communication logic
- **`vessel_controller.py`**: Manages vehicle telemetry operations
- **`main.py`**: Orchestrates application flow and lifecycle

### Object-Oriented Programming

**MQTTHandler Class:**
```python
class MQTTHandler:
    def __init__(self):
        self.broker = os.getenv('MQTT_BROKER')
        self.port = int(os.getenv('MQTT_PORT'))
        # ... initialize connection
    
    def publish(self, payload):
        # Enhanced payload with username identification
        payload_with_username = f"{payload}, USER: {self.username}"
        return payload_with_username
    
    def disconnect(self):
        # Clean resource management
```

- **Encapsulation**: All MQTT logic contained within a single class
- **State Management**: Connection details stored as instance variables
- **Enhanced Payload**: Automatically appends username for message identification

**VesselController Class:**
```python
class VesselController:
    def __init__(self, connection_string='udp:127.0.0.1:14550'):
        self.vehicle = connect(connection_string, wait_ready=True)
    
    def get_telemetry(self):
        # Same telemetry logic as before, now encapsulated
        return payload
    
    def close_connection(self):
        # Dedicated cleanup method
```

- **Single Responsibility**: Handles only vehicle operations
- **Default Parameters**: Configurable connection string with sensible defaults
- **Resource Management**: Dedicated cleanup method

### Application Orchestration

```python
def main():
    mqtt_handler = MQTTHandler()
    vessel_controller = VesselController()
    
    try:
        while True:
            telemetry_data = vessel_controller.get_telemetry()
            published_payload = mqtt_handler.publish(telemetry_data)
            print(published_payload)
            time.sleep(5)
    finally:
        vessel_controller.close_connection()
        mqtt_handler.disconnect()
```

- **Separation of Concerns**: Main function only handles application flow
- **Clear Dependencies**: Explicit initialization of required components
- **Coordinated Cleanup**: Ensures all resources are properly released

### Enhanced Error Handling

```python
try:
    self.client.connect(self.broker, self.port, 60)
    self.client.loop_start()
    print("Successfully connected to MQTT broker")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    raise
```

- **Connection Validation**: Explicit error handling for MQTT connection failures
- **Error Propagation**: Raises exceptions for calling code to handle appropriately

## SITL vs Real Hardware

**Current Setup (SITL):**
- Connection: `udp:127.0.0.1:14550` (default in VesselController)
- Modular design allows easy connection string modification

**Hardware Setup:**
- Connection: `/dev/pixhawk1` passed to VesselController constructor
- Same modular architecture works unchanged

## Architecture Benefits

- **Maintainability**: Each module has a single, clear responsibility
- **Reusability**: Classes can be imported and used in other projects
- **Testability**: Individual components can be tested in isolation
- **Scalability**: Easy to extend functionality without modifying existing code

## Running the Code

1. Ensure SITL is running with ArduPilot Rover (FRAME_CLASS=2)
2. Verify `.env` file is configured with valid MQTT settings
3. Run: `python main.py`
4. Observe same telemetry publishing behavior as Project 2
5. Press Ctrl+C to exit cleanly

## What You Will Observe

When running this script, you will see:
- Same telemetry data and MQTT publishing as Project 2
- **Enhanced payload format** with username identification
- **Improved error messages** from modular error handling
- **Clean shutdown** from coordinated resource management