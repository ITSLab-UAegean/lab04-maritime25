# Project 2: MQTT Telemetry Publishing

**Learning Objective**: Extend basic telemetry reading to publish data to an MQTT broker for remote monitoring

## Key Concepts

This project builds on Project 1's telemetry reading by adding MQTT communication capabilities.

### Environment Variable Management

```python
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
```

- **dotenv library**: Loads configuration from `.env` file located one directory above
- **Environment variables**: Separates configuration from code for different deployment environments
- **Security**: Keeps sensitive credentials out of source code

### MQTT Client Configuration

```python
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

if MQTT_USE_TLS:
    ctx = ssl.create_default_context()
    client.tls_set_context(ctx)
```

- **MQTT Client**: Enables communication with remote broker
- **Authentication**: Uses credentials from environment variables
- **TLS Security**: Configurable secure connection using system CA certificates

### Data Publishing Pattern

```python
def publish_to_mqtt(client, payload):
    result = client.publish(MQTT_TOPIC, payload)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Successfully published to MQTT.")
    else:
        print(f"Failed to publish to MQTT: {result.rc}")
```

- **Publish-Subscribe Pattern**: Vehicle publishes telemetry for remote subscribers
- **Error Handling**: Checks publish result codes for reliability
- **Topic Structure**: Uses `leader/position` for telemetry data

### MQTT Lifecycle Management

```python
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Non-blocking background thread

# ... main program logic ...

finally:
    vehicle.close()
    client.loop_stop()
    client.disconnect()
```

- **Non-blocking Operation**: `loop_start()` handles MQTT communication in background
- **Clean Shutdown**: Properly disconnects both vehicle and MQTT client

## SITL vs Real Hardware

**Current Setup (SITL):**
- Connection: `udp:127.0.0.1:14550` (local simulator)
- MQTT configuration loaded from `../.env`

**Hardware Setup:**
- Connection: `/dev/pixhawk1` (persistent device name via udev rules)
- Same MQTT broker and credentials
- Same code works with updated connection string

## Configuration

The project uses the shared `.env` file with these key variables:
- `MQTT_BROKER`: Broker hostname
- `MQTT_PORT`: Connection port (1883 or 8883 for TLS)
- `MQTT_USE_TLS`: Enable/disable secure connection
- `MQTT_USERNAME` / `MQTT_PASSWORD`: Authentication credentials

## Running the Code

1. Ensure SITL is running with ArduPilot Rover (FRAME_CLASS=2)
2. Verify `.env` file is configured with valid MQTT settings
3. Run: `python leader_telemetry.py`
4. Observe telemetry data publishing to MQTT topic `leader/position`
5. Press Ctrl+C to exit cleanly

## What You Will Observe

When running this script, you will see:
- Same telemetry data as Project 1 (GPS, heading, speed)
- **MQTT connection status** and publish confirmations
- **TLS security status** based on configuration
- **5-second intervals** of data publishing to the broker