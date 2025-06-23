# Project 1: Introduction to ArduPilot Telemetry

**Learning Objective**: Connect to an autonomous vessel and read basic sensor data

## Key Concepts

### DroneKit Library Fundamentals

```python
from dronekit import connect, VehicleMode
vehicle = connect(connection_string, wait_ready=True)
```

- **DroneKit**: Python library that provides high-level control of ArduPilot vehicles
- **`wait_ready=True`**: Critical parameter that ensures all vehicle parameters are loaded before proceeding
- **Connection string format**: `udp:127.0.0.1:14550` connects to SITL (Software In The Loop) simulator

### Vehicle Object Properties

```python
heading = vehicle.heading           # Compass direction (0-360°)
ground_speed = vehicle.groundspeed  # Speed over ground (m/s)
lat = vehicle.location.global_frame.lat  # GPS latitude
lon = vehicle.location.global_frame.lon  # GPS longitude
```

- The `vehicle` object provides real-time access to all sensor data
- **Global frame**: GPS coordinates in decimal degrees
- **Heading**: Magnetic compass bearing (important for navigation)

### Programming Patterns

**Exception Handling:**
```python
try:
    while True:
        get_telemetry()
        time.sleep(5)
except KeyboardInterrupt:
    print("Exiting script...")
finally:
    vehicle.close()
```

- **Try-except-finally**: Essential pattern for autonomous systems
- **KeyboardInterrupt**: Allows clean shutdown with Ctrl+C
- **`vehicle.close()`**: Always close connections to prevent resource leaks

## SITL vs Real Hardware

**Current Setup (SITL):**
- Connection: `udp:127.0.0.1:14550` (local simulator)
- Safe environment for learning and testing

**Hardware Setup:**
- Connection: `/dev/pixhawk1` (persistent device name via udev rules)
- udev rules ensure consistent device naming regardless of USB port or boot order
- Same code works with minimal changes by updating the connection string

## What You Will Observe

When running this script, you will see:
- **Live GPS coordinates** changing as the simulated vessel moves
- **Heading updates** as the vessel turns
- **Ground speed** measurements during movement
- **5-second intervals** demonstrating continuous monitoring

## Running the Code

1. Ensure SITL is running with ArduPilot Rover (FRAME_CLASS=2)
2. Run: `python leader_telemetry.py`
3. Observe telemetry data updating every 5 seconds
4. Press Ctrl+C to exit cleanly