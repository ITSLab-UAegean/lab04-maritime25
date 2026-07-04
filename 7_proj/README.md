# Project 7: Autonomous Following Behavior

**Learning Objectives**:
- Implement autonomous vessel following behavior using DroneKit commands
- Add Quality of Service (QoS) support for reliable MQTT communication
- Create intelligent movement detection and distance-based decision making
- Develop robust vehicle state management and mode switching
- Implement advanced navigation algorithms with safety constraints

## Key Concepts

This project implements actual autonomous following behavior that enables follower vessels to track and follow the scout vessel in real-time. Project 8 then refines it into formation keeping.

### Autonomous Following Algorithm

**Distance-Based Decision Making:**
```python
def follow_scout(self, scout_lat, scout_lon, scout_speed):
    current_distance = self.calculate_distance(
        self.vehicle.location.global_frame.lat,
        self.vehicle.location.global_frame.lon,
        scout_lat, scout_lon
    )
    
    if current_distance < self.safe_follow_distance:
        if self.vehicle.mode.name != "LOITER":
            self.vehicle.mode = VehicleMode("LOITER")
            print("Too close to scout. Loitering to maintain position.")
    else:
        # Resume following logic
```

- **Safety Distance**: Automatically keeps a minimum distance from the scout (`SAFE_FOLLOW_DISTANCE`, set in `.env`)
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
def subscribe(self, topic_names, callback, qos=None):
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

## Running the Code

**Setup** (same SITL configuration as previous projects):

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

On native Linux, macOS, or mirrored-mode WSL2, replace `[WINDOWS_HOST_IP]` with `127.0.0.1` (see Project 4). Give both boats their GPS settle time (about half a minute, until the console reports the EKF is using GPS) before sending `follow`; a `follow` before the GPS fix leaves the arming wait stuck and the vessel deaf to further commands.

Terminal 3 - Scout script:
```bash
cd ~/lab04-companion/code/7_proj
python scout.py
```

Terminal 4 - Follower script:
```bash
cd ~/lab04-companion/code/7_proj
python vessel.py vessel1
```

**Command Execution:**

Start following (replace `<broker>` with the session broker, and use your own fleet prefix; `-q 1` asks for the QoS 1 guarantee on the publish leg too):
```bash
mosquitto_pub -h <broker> -p 1883 \
  -u team1 -P team1 \
  -t 'team1/yoursurname/vessel1/commands' \
  -m '{"command": "follow"}' -q 1
```

Stop following:
```bash
mosquitto_pub -h <broker> -p 1883 \
  -u team1 -P team1 \
  -t 'team1/yoursurname/vessel1/commands' \
  -m '{"command": "stop"}' -q 1
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
```

**Active Following Behavior:**
```
Distance to scout: 42.34 meters. Mode: FOLLOWING
Issuing new goto command. Distance to scout: 42.34 meters
Distance to scout: 28.56 meters. Mode: FOLLOWING
```

**Safety Distance Activation:**
```
Distance to scout: 13.23 meters. Mode: LOITERING
Too close to scout. Loitering to maintain position.
Distance to scout: 13.15 meters. Mode: LOITERING
```

**Mission Planner Visualization:**
- Scout vessel moving under manual or autonomous control
- Follower vessel automatically following with intelligent pathfinding
- Real-time distance maintenance and safety behaviors
- Mode changes visible in vehicle status displays

## Key Features

- **Autonomous Navigation**: Follower vessels independently navigate to scout position
- **Safety Distance**: Automatic loitering when too close to scout
- **Intelligent Following**: Movement detection prevents unnecessary navigation commands
- **Real-time Response**: Immediate reaction to scout position changes
- **Reliable Commands**: QoS 1 ensures critical follow/stop commands are delivered
- **State Management**: Proper vehicle arming and mode control
- **Mission Planner Integration**: Visual monitoring of autonomous behavior

This project demonstrates a complete autonomous maritime system with real-time coordination, safety features, and professional-grade navigation algorithms.