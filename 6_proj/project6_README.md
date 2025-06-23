# Project 6: Command Processing System

**Learning Objectives**:
- Implement multi-topic MQTT subscription for team vessels
- Add command processing capabilities for remote vessel control
- Handle both JSON and plain text command formats
- Create a foundation for autonomous behavior control

## Key Concepts

This project extends the publisher-subscriber system from Project 5 by adding command processing capabilities to team vessels, enabling remote control and coordination.

### Multi-Topic Subscription

**Enhanced Subscription Pattern:**
```python
# Create a list of topics to subscribe to
topics_to_subscribe = ['SCOUT_POSITION_TOPIC', f'{team.upper()}_COMMANDS']

# Subscribe to topics
mqtt_handler.subscribe(topics_to_subscribe)
```

- **Multiple subscriptions**: Team vessels now listen to both scout position and their own command topic
- **Dynamic topic construction**: Command topics are built based on vessel role (e.g., `team1/commands`)
- **Centralized subscription**: Single method call handles multiple topic subscriptions

### Flexible Subscription Handler

**Multi-Topic Support:**
```python
def subscribe(self, topic_names):
    # Handle single topic or list of topics
    if isinstance(topic_names, str):
        topic_names = [topic_names]
        
    for topic_name in topic_names:
        topic = os.getenv(topic_name)
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, self.on_message)
        print(f"Subscribed to topic: {topic}")
```

- **Backward compatibility**: Accepts both single topics and topic lists
- **Environment variable resolution**: Resolves topic names from configuration
- **Unified callback**: Single message handler for all subscribed topics

### Enhanced Message Processing

**Intelligent Message Routing:**
```python
def on_message(self, client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
        if 'latitude' in payload and 'longitude' in payload:
            print(f"  Latitude: {payload['latitude']}, Longitude: {payload['longitude']}")
        elif msg.topic.lower().endswith('commands'):
            command = payload.get('command', '').lower()
            self.handle_command(command)
        else:
            print(f"  Payload: {payload}")
            
    except json.JSONDecodeError:
        # Fallback to plain text command processing
        if msg.topic.lower().endswith('commands'):
            command = msg.payload.decode().strip().lower()
            self.handle_command(command)
```

- **Content-aware routing**: Different handling based on message content
- **Position data processing**: Continues to handle scout position updates
- **Command detection**: Recognizes command topics by naming convention
- **Dual format support**: Handles both JSON and plain text commands

### Command Processing System

**Command Handler:**
```python
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
```

- **Command recognition**: Processes "follow" and "stop" commands
- **Visual feedback**: Prominent display of received commands
- **Extensible design**: Easy to add new command types
- **Unknown command handling**: Graceful handling of unrecognized commands

### Command Topic Configuration

From `.env` file:
```
TEAM1_COMMANDS=team1/commands
TEAM2_COMMANDS=team2/commands
TEAM3_COMMANDS=team3/commands
```

- **Role-specific channels**: Each team vessel has its own command topic
- **Individual control**: Commands can be sent to specific vessels
- **Scalable architecture**: Easy to add more team vessels

## SITL Configuration

Same multi-vehicle SITL setup as Projects 4-5. No changes to the underlying simulation infrastructure.

## Running the Code

**Script Execution** (same as Project 5):

Terminal 1 - Scout:
```bash
cd ~/lab04-companion/code/6_proj
python scout.py
```

Terminal 2 - Team vessel:
```bash
cd ~/lab04-companion/code/6_proj
python team.py team1
```

**Command Testing:**

Send commands via MQTT:
```bash
# JSON format command
mosquitto_pub -h smartmove-local.syros.aegean.gr -p 1883 \
  -u team1 -P team1 \
  -t team1/commands \
  -m '{"command": "follow"}'

# Plain text command
mosquitto_pub -h smartmove-local.syros.aegean.gr -p 1883 \
  -u team1 -P team1 \
  -t team1/commands \
  -m "stop"
```

## What You Will Observe

**Team Vessel Startup:**
```
Starting team1 vessel...
TLS enabled, using system default CA certificates
Successfully connected to MQTT broker
Subscribed to topic: scout/position
Subscribed to topic: team1/commands
Connecting to vehicle on: udp:127.0.0.1:14560
```

**Position Data Reception:**
```
{"timestamp": "23/06/2025 - 11:45:15", "heading": 180, "ground_speed": 0.00, "latitude": 37.438788, "longitude": 24.945544, "boat": "team1"}
Successfully published to MQTT topic: team1/position
Received message on topic scout/position:
  Latitude: 37.438788, Longitude: 24.945544
```

**Command Reception:**
```
**************************************************
Command to start following is issued
**************************************************
```

**Key Features:**
- **Dual subscription**: Team vessels receive both position updates and commands
- **Command acknowledgment**: Visual confirmation when commands are received
- **Format flexibility**: Accepts both JSON and plain text command formats
- **Foundation for automation**: Infrastructure ready for autonomous behavior implementation

## Architecture Benefits

- **Remote Control**: Enables external systems to send commands to specific vessels
- **Command Acknowledgment**: Clear feedback when commands are received and processed
- **Flexible Communication**: Supports multiple message formats and content types
- **Autonomous Foundation**: Prepares infrastructure for implementing following behavior in future projects