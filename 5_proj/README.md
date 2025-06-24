# Project 5: Publisher-Subscriber Communication

**Learning Objectives**:
- Implement MQTT publisher-subscriber pattern for inter-vessel communication
- Use JSON data format for structured telemetry exchange
- Create dedicated execution scripts for different vessel types
- Enable team vessels to receive and process scout position data

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

**Team Vessels (`team.py`):**
```python
parser.add_argument('team', choices=['team1', 'team2', 'team3'], 
                   help='Team vessel role (team1, team2, or team3)')
mqtt_handler.subscribe('SCOUT_POSITION_TOPIC')
```

- **Role-specific scripts**: Scout and team vessels have different execution patterns
- **Subscription pattern**: Team vessels automatically subscribe to scout position updates
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
    payload['boat'] = self.username  # Add vessel identifier
    json_payload = json.dumps(payload)  # Serialize to JSON
    result = self.client.publish(self.topic, json_payload)
    return json_payload
```

- **Boat identification**: Automatically adds vessel identifier to messages
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
Scout → Publishes to scout/position → MQTT Broker
Team Vessels → Subscribe to scout/position → Receive updates
Team Vessels → Publish to team1/position, team2/position, team3/position
```

- **One-to-many communication**: Scout broadcasts position to all team vessels
- **Asynchronous messaging**: Vessels receive updates without blocking main loops
- **Scalable architecture**: Easy to add more subscribers without code changes

## Configuration Requirements

Same `.env` configuration as Project 4, with the addition that team vessels automatically subscribe to:
```
SCOUT_POSITION_TOPIC=scout/position
```

## Running the Code

**Terminal Setup** (same SITL configuration as Project 4):

Terminal 1 - Scout SITL:
```bash
cd ~/sitl-test
sim_vehicle.py -v Rover -L Syros --add-param-file=/home/thomas/custom-parms/boat.parm --out=udp:127.0.0.1:14550 --console --map
```

Terminal 2 - Team SITL:
```bash
cd ~/sitl-test2
sim_vehicle.py -v Rover -L Syros2 --add-param-file=/home/thomas/custom-parms/boat.parm --instance 1 --console --map --sysid=2 --out=udp:127.0.0.1:14560 --out=udp:[WINDOWS_HOST_IP]:14550
```

**Script Execution:**

Terminal 3 - Scout:
```bash
cd ~/lab04-companion/code/5_proj
python scout.py
```

Terminal 4 - Team vessel:
```bash
cd ~/lab04-companion/code/5_proj
python team.py team1
```

## What You Will Observe

**Scout Output:**
```
Starting scout vessel...
TLS enabled, using system default CA certificates
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14550
{"timestamp": "23/06/2025 - 11:45:12", "heading": 180, "ground_speed": 0.02, "latitude": 37.438788, "longitude": 24.945544, "boat": "scout"}
Successfully published to MQTT topic: scout/position
```

**Team Output:**
```
Starting team1 vessel...
TLS enabled, using system default CA certificates
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14560
{"timestamp": "23/06/2025 - 11:45:15", "heading": 180, "ground_speed": 0.00, "latitude": 37.438788, "longitude": 24.945544, "boat": "team1"}
Successfully published to MQTT topic: team1/position
Received message on topic scout/position:
  Latitude: 37.438788, Longitude: 24.945544
```

**Key Features:**
- **JSON formatted messages** instead of text strings
- **Automatic subscription** - team vessels receive scout position updates
- **Boat identification** in every published message
- **Real-time position sharing** between scout and team vessels

## Architecture Benefits

- **Structured Data**: JSON format enables programmatic processing of telemetry
- **Inter-vessel Awareness**: Team vessels can track scout position in real-time
- **Foundation for Coordination**: Sets up infrastructure for future autonomous following behavior
- **Separation of Concerns**: Clear distinction between publisher (scout) and subscriber (team) roles