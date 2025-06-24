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
parser.add_argument('role', choices=['scout', 'team1', 'team2', 'team3'], 
                   help='Vessel role (scout, team1, team2, or team3)')
```

- **argparse Module**: Professional command-line argument handling
- **Role Validation**: Restricts input to valid vessel roles (scout, team1, team2, team3)
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
Python scripts → Localhost ports (14550, 14560) → Individual SITL instances
SITL instances → Windows host IP:14550 → Mission Planner  
SITL instances → MQTT broker → Inter-vessel communication
```

**SITL Instance Setup:**

Terminal 1 - Scout:
```bash
cd ~/sitl-test
sim_vehicle.py -v Rover -L Syros \
--add-param-file=/home/thomas/custom-parms/boat.parm \
--out=udp:127.0.0.1:14550 --console --map
```

Terminal 2 - Team1:
```bash
cd ~/sitl-test2
sim_vehicle.py -v Rover -L Syros2 \
--add-param-file=/home/thomas/custom-parms/boat.parm \
--instance 1 --console --map --sysid=2 \
--out=udp:127.0.0.1:14560 --out=udp:[WINDOWS_HOST_IP]:14550
```

**Key Parameters:**
- **`--instance 1`**: Creates second vehicle instance
- **`--sysid=2`**: Assigns unique system ID for Mission Planner
- **Multiple outputs**: Local for Python scripts, Windows host for Mission Planner

### Mission Planner Integration

**Connection Flow:**
- Both vehicles appear in Mission Planner with System IDs 1 (Scout) and 2 (Team1)
- Mission Planner connects via UDP to port 14550 on Windows host
- Unified visualization of all vehicles simultaneously

**MAVProxy Network Outputs:**
- MAVProxy automatically detects WSL2 and adds Windows host outputs
- Manual correction may be needed for proper Mission Planner port mapping

## Configuration Requirements

The `.env` file must contain role-specific variables:

```
SCOUT_MQTT_USERNAME=scout
SCOUT_MQTT_PASSWORD=scout
SCOUT_POSITION_TOPIC=scout/position
SCOUT_CONNECTION_STRING=udp:127.0.0.1:14550

TEAM1_MQTT_USERNAME=team1
TEAM1_MQTT_PASSWORD=team1
TEAM1_POSITION_TOPIC=team1/position
TEAM1_CONNECTION_STRING=udp:127.0.0.1:14560
```

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

Terminal 4 - Team1:
```bash
cd ~/lab04-companion/code/4_proj
python main.py team1
```

**Monitoring All Vessels:**
```bash
mosquitto_sub -h smartmove-local.syros.aegean.gr -p 1883 \
  -u scout -P scout \
  -t scout/position -t team1/position -t team2/position -t team3/position -v
```

## What You Will Observe

**Scout Output:**
```
TLS enabled, using system default CA certificates
Connecting to smartmove-local.syros.aegean.gr:8883 ...
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14550
Successfully published to MQTT topic: scout/position
```

**Team1 Output:**
```
TLS enabled, using system default CA certificates
Connecting to smartmove-local.syros.aegean.gr:8883 ...
Successfully connected to MQTT broker
Connecting to vehicle on: udp:127.0.0.1:14560
Successfully published to MQTT topic: team1/position
```

**Key Features:**
- **Role identification** in all output messages
- **Role-specific MQTT topics** (scout/position, team1/position)
- **Independent vehicle connections** on different UDP ports
- **Mission Planner integration** showing both vehicles with unique system IDs

## Architecture Benefits

- **Independent Control**: Each vessel operates with separate programmatic control
- **Unified Visualization**: Mission Planner displays all vehicles simultaneously  
- **Inter-vessel Communication**: Real-time coordination via MQTT
- **Scalability**: Easy addition of more vessels through environment variables