# Project 4: Multi-Vessel Role-Based System

**Learning Objectives**: 
- Implement role-based vehicle control
- Use command-line arguments for configuration  
- Dynamically load environment variables based on role
- Enable multi-vehicle simulation scenarios
- Configure WSL2 multi-vehicle SITL with Mission Planner integration

## Key Concepts

This project extends the modular architecture from Project 3 to support multiple vessels with different roles, WSL2 networking, and Mission Planner integration.

### Role-Based Configuration System

**Command-Line Interface:**
```python
parser = argparse.ArgumentParser(description='Multi-vessel telemetry system')
parser.add_argument('role', choices=['scout', 'vessel1', 'vessel2', 'vessel3'],
                   help='Vessel role (scout, vessel1, vessel2, or vessel3)')
```

- **argparse Module**: Professional command-line argument handling
- **Role Validation**: Restricts input to valid vessel roles (scout, vessel1, vessel2, vessel3)
- **Deployment Flexibility**: Same codebase supports different vessel configurations

### Dynamic Environment Variable Resolution

**MQTTHandler Role-based Configuration:**
```python
def __init__(self, role):
    self.role = role.upper()
    self.username = os.getenv(f'{self.role}_MQTT_USERNAME')
    self.password = os.getenv(f'{self.role}_MQTT_PASSWORD')
    self.topic = os.getenv(f'{self.role}_POSITION_TOPIC')
```

- **Dynamic Variable Names**: Constructs environment variable names based on role
- **Role-Specific Credentials**: Each vessel uses unique MQTT authentication
- **Topic Separation**: Each role publishes to its own MQTT topic

**VesselController Role-based Connection:**
```python
def get_connection_string(self):
    connection_string = os.getenv(f'{self.role}_CONNECTION_STRING')
    if not connection_string:
        raise ValueError(f"Missing connection string for role: {self.role}")
    return connection_string
```

- **Connection String Mapping**: Each role connects to its assigned vehicle
- **Multi-SITL Support**: Different UDP ports for simultaneous simulation

### WSL2 Multi-Vehicle SITL Configuration

**Network Architecture:**
```
Python scripts → Localhost ports (14551, 14561) → Individual SITL instances
SITL instances → GCS copy on port 14550 → Mission Planner
SITL instances → MQTT broker → Inter-vessel communication
```

The standard port 14550 belongs to the graphical ground station (Mission Planner or QGroundControl); each boat's Python reads a private localhost port instead, the boat's instance default + 1 (scout 14551, vessel1 14561). Every boat therefore launches with two `--out` flags.

**SITL Instance Setup:**

Terminal 1 - Scout:
```bash
cd ~/maritime26/sitl-test
sim_vehicle.py -v Rover -L Syros \
  --add-param-file=$HOME/maritime26/custom-parms/boat.parm \
  --out=udp:[WINDOWS_HOST_IP]:14550 --out=udp:127.0.0.1:14551
```

Terminal 2 - Vessel1:
```bash
cd ~/maritime26/sitl-test2
sim_vehicle.py -v Rover --instance 1 --sysid 2 -L Syros2 \
  --add-param-file=$HOME/maritime26/custom-parms/boat.parm \
  --out=udp:[WINDOWS_HOST_IP]:14550 --out=udp:127.0.0.1:14561
```

On native Linux, macOS, or mirrored-mode WSL2, replace `[WINDOWS_HOST_IP]` with `127.0.0.1`; the ground station listens on the same machine. See the Lab 03 notes for `boat.parm` and the SITL working folders.

**Key Parameters:**
- **`--instance 1`**: Creates second vehicle instance
- **`--sysid 2`**: Assigns unique system ID for Mission Planner
- **Two outputs per boat**: the ground-station copy on 14550, the boat's own Python port (instance default + 1)

### Mission Planner Integration

**Connection Flow:**
- Both vehicles appear in Mission Planner with System IDs 1 (Scout) and 2 (Vessel1)
- Mission Planner connects via UDP to port 14550 on Windows host
- Unified visualization of all vehicles simultaneously

**MAVProxy Network Outputs:**
- The two explicit `--out` flags above make the routing deterministic; nothing relies on MAVProxy's WSL2 auto-detection

## Configuration Requirements

The `.env` file must contain role-specific variables:

```
TEAM_NS=team1
FLEET_NS=${TEAM_NS}/yoursurname

SCOUT_MQTT_USERNAME=${TEAM_NS}
SCOUT_MQTT_PASSWORD=${TEAM_NS}
SCOUT_POSITION_TOPIC=${FLEET_NS}/scout/position
SCOUT_CONNECTION_STRING=udp:127.0.0.1:14551

VESSEL1_MQTT_USERNAME=${TEAM_NS}
VESSEL1_MQTT_PASSWORD=${TEAM_NS}
VESSEL1_POSITION_TOPIC=${FLEET_NS}/vessel1/position
VESSEL1_CONNECTION_STRING=udp:127.0.0.1:14561
```

`TEAM_NS` is your team id (it selects the shared team login); `FLEET_NS` prefixes every topic with team + surname, so each running fleet stays isolated on the shared broker. See `.env.example` for the full commented layout.

## Running the Code

**Prerequisites:**
1. Find Windows host IP: `ip route show | grep -i default | awk '{ print $3}'`
2. Start SITL instances in separate terminals (as shown above)
3. Connect Mission Planner to UDP port 14550

**Execution:**

Terminal 3 - Scout:
```bash
cd ~/lab04-companion/code/4_proj
python main.py scout
```

Terminal 4 - Vessel1:
```bash
cd ~/lab04-companion/code/4_proj
python main.py vessel1
```

**Monitoring All Vessels** (everything under your fleet prefix):
```bash
mosquitto_sub -h <broker> -p 1883 -u team1 -P team1 \
  -t 'team1/yoursurname/#' -v
```

## What You Will Observe

**Scout Output:**
```
TLS disabled, using non-secure connection
Connecting to <broker>:1883 ...
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14551
Successfully published to MQTT topic: team1/yoursurname/scout/position
```

**Vessel1 Output:**
```
TLS disabled, using non-secure connection
Connecting to <broker>:1883 ...
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14561
Successfully published to MQTT topic: team1/yoursurname/vessel1/position
```

**Key Features:**
- **Role identification** in all output messages
- **Role-specific MQTT topics** under the fleet prefix (`.../scout/position`, `.../vessel1/position`)
- **Independent vehicle connections** on different UDP ports
- **Mission Planner integration** showing both vehicles with unique system IDs

## Architecture Benefits

- **Independent Control**: Each vessel operates with separate programmatic control
- **Unified Visualization**: Mission Planner displays all vehicles simultaneously  
- **Inter-vessel Communication**: Real-time coordination via MQTT
- **Scalability**: Easy addition of more vessels through environment variables