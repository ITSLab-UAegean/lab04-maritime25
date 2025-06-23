# Project 7: Autonomous Following Behavior

**Learning Objectives**:
- Implement autonomous vessel following behavior using DroneKit commands
- Add Quality of Service (QoS) support for reliable MQTT communication
- Create intelligent movement detection and distance-based decision making
- Develop robust vehicle state management and mode switching
- Implement advanced navigation algorithms with safety constraints

## Key Concepts

This project represents the culmination of the series, implementing actual autonomous following behavior that enables team vessels to track and follow the scout vessel in real-time.

### Autonomous Following Algorithm

**Distance-Based Decision Making:**
```python
def follow_scout(self, scout_lat, scout_lon, scout_speed):
    current_distance = self.calculate_distance(
        self.vehicle.location.global_frame.lat,
        self.vehicle.location.global_frame.lon,
        scout_lat, scout_lon
    )
    
    if current_distance < 5:
        if self.vehicle.mode.name != "LOITER":
            self.vehicle.mode = VehicleMode("LOITER")
            print("Too close to scout. Loitering to maintain position.")
    else:
        # Resume following logic
```

- **Safety Distance**: Automatically maintains 5-meter minimum distance from scout
- **Mode Switching**: Dynamically switches between GUIDED (following) and LOITER (holding position)
- **Real-time Decision Making**: Continuously evaluates distance and adjusts behavior

### Intelligent Movement Detection

**Scout Movement Analysis:**
```python
def scout_has_moved(self, scout_lat, scout_lon, scout_speed):
    distance_moved = self.calculate_distance(
        self.last_goto_position[0], self.last_goto_position[1],
        scout_lat, scout_lon
    )
    
    self.scout_speeds.append(scout_speed)
    avg_speed = sum(self.scout_speeds) / len(self.scout_speeds)
    
    # Consider scout moved if position changed >4m OR average speed >0.5 m/s
    return distance_moved > 4 or avg_speed > 0.5
```

- **Position Change Detection**: Tracks scout position changes greater than 4 meters
- **Speed Averaging**: Uses rolling average of last 3 speed readings
- **Dual Criteria**: Movement detected by either position change or sustained speed
- **Prevents Unnecessary Commands**: Avoids sending goto commands when scout is stationary

### Advanced Navigation Control

**Goto Command Optimization:**
```python
should_update = (
    self.last_goto_position is None or
    current_time - self.last_goto_time >= 15 or
    current_distance > self.last_scout_distance + 5
)

if should_update and self.scout_has_moved(scout_lat, scout_lon, scout_speed):
    self.vehicle.simple_goto(LocationGlobalRelative(scout_lat, scout_lon, 0))
    self.last_goto_time = current_time
    self.last_goto_position = (scout_lat, scout_lon)
```

- **Time-based Updates**: New goto commands every 15 seconds maximum
- **Distance Triggers**: Updates when distance increases significantly
- **Position Tracking**: Records last goto position to detect scout movement
- **DroneKit Integration**: Uses `simple_goto` for actual vehicle navigation

### Quality of Service (QoS) Implementation

**Message Priority System:**
```python
def subscribe(self, topic_names, callback=None, qos=None):
    if 'commands' in topic_name.lower():
        topic_qos = 1  # QoS 1 for commands (guaranteed delivery)
    else:
        topic_qos = 0  # QoS 0 for telemetry/positions
    
    self.client.subscribe(topic, qos=topic_qos)
```

- **Command Reliability**: QoS 1 ensures command messages are delivered
- **Telemetry Efficiency**: QoS 0 for frequent position updates (best effort)
- **Automatic QoS Selection**: Intelligent QoS assignment based on topic type
- **Manual Override**: Support for explicit QoS specification

### Custom MQTT Integration

**Direct Vehicle Control:**
```python
def on_message(client, userdata, msg):
    vessel_controller = userdata['vessel_controller']
    
    if 'latitude' in payload and 'longitude' in payload and 'ground_speed' in payload:
        if vessel_controller.following:
            vessel_controller.follow_scout(
                payload['latitude'],
                payload['longitude'], 
                payload['ground_speed']
            )
```

- **User Data Passing**: Vessel controller passed through MQTT user data
- **Real-time Response**: Position updates immediately trigger following behavior
- **State-aware Processing**: Only follows when in following mode
- **Direct Integration**: MQTT callbacks directly control vehicle behavior

### Vehicle State Management

**Mode Control and Arming:**
```python
def arm_vehicle(self):
    if not self.vehicle.armed:
        print("Arming vehicle...")
        self.vehicle.armed = True
        while not self.vehicle.armed:
            time.sleep(1)

def set_guided_mode(self):
    self.vehicle.mode = VehicleMode("GUIDED")
    while self.vehicle.mode.name != "GUIDED":
        time.sleep(1)
    self.following = True
```

- **Safe Arming**: Ensures vehicle is armed before accepting navigation commands
- **Mode Verification**: Waits for mode changes to complete before proceeding
- **State Synchronization**: Following flag tracks autonomous behavior state
- **DroneKit Integration**: Uses standard ArduPilot vehicle modes

### Enhanced Error Handling

**MQTT Reconnection Logic:**
```python
except struct.error:
    print("Encountered a malformed MQTT message. Attempting to reconnect...")
    mqtt_handler.client.disconnect()
    time.sleep(5)
    try:
        mqtt_handler.client.reconnect()
        mqtt_handler.subscribe(topics_to_subscribe, on_message)
    except Exception as e:
        print(f"Reconnection failed: {e}")
```

- **Malformed Message Recovery**: Handles corrupt MQTT data gracefully
- **Automatic Reconnection**: Attempts to restore MQTT connectivity
- **Resubscription**: Restores topic subscriptions after reconnection
- **Graceful Degradation**: Continues operation despite communication issues

## Running the Code

**Setup** (same SITL configuration as previous projects):

Terminal 1 - Scout SITL and script:
```bash
# Start SITL
cd ~/sitl-test
sim_vehicle.py -v Rover -L Syros --add-param-file=/home/thomas/custom-parms/boat.parm --out=udp:127.0.0.1:14550 --console --map

# Run scout script
cd ~/lab04-companion/code/7_proj
python scout.py
```

Terminal 2 - Team SITL and script:
```bash
# Start SITL
cd ~/sitl-test2
sim_vehicle.py -v Rover -L Syros2 --add-param-file=/home/thomas/custom-parms/boat.parm --instance 1 --console --map --sysid=2 --out=udp:127.0.0.1:14560 --out=udp:[WINDOWS_HOST_IP]:14550

# Run team script
cd ~/lab04-companion/code/7_proj
python team.py team1
```

**Command Execution:**

Start following:
```bash
mosquitto_pub -h smartmove-local.syros.aegean.gr -p 1883 \
  -u team1 -P team1 \
  -t team1/commands \
  -m '{"command": "follow"}'
```

Stop following:
```bash
mosquitto_pub -h smartmove-local.syros.aegean.gr -p 1883 \
  -u team1 -P team1 \
  -t team1/commands \
  -m '{"command": "stop"}'
```

## What You Will Observe

**Follow Command Response:**
```
**************************************************
Command to start following is issued
**************************************************
Arming vehicle...
Vehicle armed.
Vehicle is in GUIDED mode. Started following.
Team vessel ready. Waiting for commands...
```

**Active Following Behavior:**
```
Distance to scout: 12.34 meters. Mode: FOLLOWING
Issuing new goto command. Distance to scout: 12.34 meters
Received message on topic scout/position:
  Latitude: 37.438788, Longitude: 24.945544
Distance to scout: 8.56 meters. Mode: FOLLOWING
```

**Safety Distance Activation:**
```
Distance to scout: 4.23 meters. Mode: LOITERING
Too close to scout. Loitering to maintain position.
Distance to scout: 4.15 meters. Mode: LOITERING
```

**Mission Planner Visualization:**
- Scout vessel moving under manual or autonomous control
- Team vessel automatically following with intelligent pathfinding
- Real-time distance maintenance and safety behaviors
- Mode changes visible in vehicle status displays

## Key Features

- **Autonomous Navigation**: Team vessels independently navigate to scout position
- **Safety Distance**: Automatic loitering when too close to scout
- **Intelligent Following**: Movement detection prevents unnecessary navigation commands
- **Real-time Response**: Immediate reaction to scout position changes
- **Reliable Commands**: QoS 1 ensures critical follow/stop commands are delivered
- **State Management**: Proper vehicle arming and mode control
- **Mission Planner Integration**: Visual monitoring of autonomous behavior

This project demonstrates a complete autonomous maritime system with real-time coordination, safety features, and professional-grade navigation algorithms.