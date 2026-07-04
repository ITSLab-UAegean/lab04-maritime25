# Project 5: Publisher-Subscriber Communication

**Learning Objectives**:
- Implement MQTT publisher-subscriber pattern for inter-vessel communication
- Use JSON data format for structured telemetry exchange
- Create dedicated execution scripts for different vessel types
- Enable follower vessels to receive and process scout position data

## Key Concepts

This project extends the multi-vessel architecture from Project 4 by adding MQTT subscription capabilities and structured JSON messaging.

### Separate Execution Architecture

**Scout Vessel (`scout.py`):**
```python
def main():
    print("Starting scout vessel...")
    mqtt_handler = MQTTHandler('SCOUT')
    vessel_controller = VesselController('SCOUT')
```

**Follower Vessels (`vessel.py`):**
```python
parser.add_argument('role', choices=['vessel1', 'vessel2', 'vessel3'],
                   help='Vessel role (vessel1, vessel2, or vessel3)')
mqtt_handler.subscribe('SCOUT_POSITION_TOPIC')
```

- **Role-specific scripts**: Scout and follower vessels have different execution patterns
- **Subscription pattern**: Follower vessels automatically subscribe to scout position updates
- **Simplified deployment**: Clear separation between scout and follower roles

### JSON Data Structure

**Structured Telemetry Data:**
```python
def get_telemetry(self):
    telemetry_data = {
        "timestamp": timestamp,
        "heading": self.vehicle.heading,
        "ground_speed": round(self.vehicle.groundspeed, 2),
        "latitude": self.vehicle.location.global_frame.lat,
        "longitude": self.vehicle.location.global_frame.lon
    }
    return telemetry_data
```

- **Dictionary format**: Replaces formatted string with structured data
- **Type preservation**: Maintains numeric types for mathematical operations
- **Standardized fields**: Consistent data structure across all vessels

### MQTT Publishing with JSON

**Enhanced Publishing:**
```python
def publish(self, payload):
    payload['boat'] = self.role.lower()  # Add vessel identifier (its role)
    json_payload = json.dumps(payload)  # Serialize to JSON
    result = self.client.publish(self.topic, json_payload)
    return json_payload
```

- **Boat identification**: Automatically adds the vessel's role to messages (every boat in a team shares the team login, so the username would not identify the boat)
- **JSON serialization**: Converts Python dictionary to JSON string
- **Structured messaging**: Enables programmatic processing by subscribers

### MQTT Subscription System

**Subscription Setup:**
```python
def subscribe(self, topic_name, callback=None):
    topic = os.getenv(topic_name)
    if not topic:
        raise ValueError(f"Missing {topic_name} in environment variables")
    
    self.client.subscribe(topic)
    self.client.message_callback_add(topic, callback or default_callback)
```

**Default Message Handler:**
```python
def default_callback(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received message on topic {msg.topic}:")
        print(f"  Latitude: {payload.get('latitude')}, Longitude: {payload.get('longitude')}")
    except json.JSONDecodeError:
        print("Received invalid JSON message")
```

- **Dynamic topic resolution**: Subscribes to topics defined in environment variables
- **JSON parsing**: Automatically deserializes received messages
- **Error handling**: Graceful handling of malformed JSON messages
- **Callback pattern**: Supports custom message handlers

### Publisher-Subscriber Pattern

**Communication Flow:**
```
Scout → Publishes to <FLEET_NS>/scout/position → MQTT Broker
Followers → Subscribe to <FLEET_NS>/scout/position → Receive updates
Followers → Publish to <FLEET_NS>/vessel1/position, .../vessel2/position, .../vessel3/position
```

- **One-to-many communication**: Scout broadcasts position to all follower vessels
- **Asynchronous messaging**: Vessels receive updates without blocking main loops
- **Scalable architecture**: Easy to add more subscribers without code changes

## Configuration Requirements

Same `.env` configuration as Project 4, with the addition that follower vessels automatically subscribe to:
```
SCOUT_POSITION_TOPIC=${FLEET_NS}/scout/position
```

## Running the Code

**Terminal Setup** (same SITL configuration as Project 4):

Terminal 1 - Scout SITL:
```bash
cd ~/maritime26/sitl-test
sim_vehicle.py -v Rover -L Syros \
  --add-param-file=$HOME/maritime26/custom-parms/boat.parm \
  --out=udp:[WINDOWS_HOST_IP]:14550 --out=udp:127.0.0.1:14551
```

Terminal 2 - Vessel1 SITL:
```bash
cd ~/maritime26/sitl-test2
sim_vehicle.py -v Rover --instance 1 --sysid 2 -L Syros2 \
  --add-param-file=$HOME/maritime26/custom-parms/boat.parm \
  --out=udp:[WINDOWS_HOST_IP]:14550 --out=udp:127.0.0.1:14561
```

On native Linux, macOS, or mirrored-mode WSL2, replace `[WINDOWS_HOST_IP]` with `127.0.0.1` (see Project 4).

**Script Execution:**

Terminal 3 - Scout:
```bash
cd ~/lab04-companion/code/5_proj
python scout.py
```

Terminal 4 - Follower vessel:
```bash
cd ~/lab04-companion/code/5_proj
python vessel.py vessel1
```

## What You Will Observe

**Scout Output:**
```
Starting scout vessel...
TLS disabled, using non-secure connection
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14551
{"timestamp": "23/06/2026 - 11:45:12", "heading": 180, "ground_speed": 0.02, "latitude": 37.438788, "longitude": 24.945544, "boat": "scout"}
Successfully published to MQTT topic: team1/yoursurname/scout/position
```

**Follower Output:**
```
Starting vessel1 vessel...
TLS disabled, using non-secure connection
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14561
{"timestamp": "23/06/2026 - 11:45:15", "heading": 180, "ground_speed": 0.00, "latitude": 37.438788, "longitude": 24.945544, "boat": "vessel1"}
Successfully published to MQTT topic: team1/yoursurname/vessel1/position
Received message on topic team1/yoursurname/scout/position:
  Latitude: 37.438788, Longitude: 24.945544
```

**Key Features:**
- **JSON formatted messages** instead of text strings
- **Automatic subscription** - follower vessels receive scout position updates
- **Boat identification** in every published message
- **Real-time position sharing** between scout and follower vessels

## Architecture Benefits

- **Structured Data**: JSON format enables programmatic processing of telemetry
- **Inter-vessel Awareness**: Follower vessels can track scout position in real-time
- **Foundation for Coordination**: Sets up infrastructure for future autonomous following behavior
- **Separation of Concerns**: Clear distinction between publisher (scout) and subscriber (follower) roles