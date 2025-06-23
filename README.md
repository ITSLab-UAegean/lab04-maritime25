# Maritime Informatics & Robotics Summer School - 2025


A comprehensive hands-on workshop for learning autonomous vessel programming using Python, DroneKit, and ArduPilot Rover firmware configured for maritime applications (FRAME_CLASS=2).

## Lab04 Code Repository

This repository contains 7 progressive projects that take you from basic telemetry reading to implementing autonomous multi-vessel coordination systems. Each project builds upon the previous one, introducing new concepts while maintaining a professional software architecture.

### Learning Progression

- **Project 1**: Basic telemetry reading with DroneKit
- **Project 2**: MQTT telemetry publishing for remote monitoring
- **Project 3**: Modular object-oriented architecture
- **Project 4**: Multi-vessel role-based system with WSL2 integration
- **Project 5**: Publisher-subscriber communication with JSON messaging
- **Project 6**: Command processing for remote vessel control
- **Project 7**: Autonomous following behavior and coordination

## Prerequisites

### Software Requirements

- **WSL2** (Windows Subsystem for Linux) or native Linux environment
- **ArduPilot SITL** (Software In The Loop) simulator
- **Mission Planner** for ground control and visualization
- **Python 3.8+** with virtual environment support

### Python Dependencies

Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv ss_venv

# Activate virtual environment
# On Linux/WSL:
source ss_venv/bin/activate
# On Windows:
# ss_venv\Scripts\activate
```

Install required packages:
```bash
pip install -r requirements.txt
```

### Hardware Requirements (Optional)

For real deployment after simulation:
- **Pixhawk 2.4.8 PX4 Flight Controller** running ArduPilot Rover
- **Raspberry Pi 5 (8GB)** as companion computer
- **Maritime vessel platform** for autonomous operations

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repository-url>
cd lab04-companion/code
```

### 2. Environment Configuration

Create your `.env` file in the root directory with the following structure:

```bash
cp .env.example .env
# Edit .env with your specific MQTT broker settings
```

Required environment variables:
- MQTT broker connection details
- Role-specific credentials (scout, team1, team2, team3)
- Connection strings for SITL instances
- TLS certificate configuration

### 3. SITL Setup

Each project requires running ArduPilot SITL instances. Basic setup:

```bash
# Scout vehicle
sim_vehicle.py -v Rover -L Syros \
--add-param-file=/path/to/boat.parm \
--out=udp:127.0.0.1:14550 --console --map

# Team vehicle (for multi-vessel projects)
sim_vehicle.py -v Rover -L Syros2 \
--add-param-file=/path/to/boat.parm \
--instance 1 --console --map --sysid=2 \
--out=udp:127.0.0.1:14560 --out=udp:[WINDOWS_HOST_IP]:14550
```

### 4. Mission Planner Integration

Connect Mission Planner to UDP port 14550 to visualize all vehicles simultaneously with unique system IDs.

## Project Structure

```
├── 1_proj/           # Basic telemetry reading
├── 2_proj/           # MQTT telemetry publishing
├── 3_proj/           # Modular architecture
├── 4_proj/           # Multi-vessel system
├── 5_proj/           # Publisher-subscriber communication
├── 6_proj/           # Command processing
├── 7_proj/           # Autonomous following behavior
├── .env.example      # Environment template
├── ca.crt           # MQTT broker certificate
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

Each project directory contains:
- Complete source code for that project's functionality
- Individual README.md with detailed technical explanations
- Shared modules (mqtt_handler.py, vessel_controller.py, etc.)

## Key Concepts Covered

### Programming Concepts
- DroneKit library for autopilot control
- MQTT publisher-subscriber patterns
- Object-oriented architecture and modularity
- Environment variable management
- JSON data serialization
- Quality of Service (QoS) in messaging systems

### Autonomous Systems Concepts
- Vehicle state management and mode switching
- Real-time telemetry processing
- Inter-vessel communication protocols
- Distance-based decision making
- Safety constraints and collision avoidance
- Autonomous navigation with ArduPilot

### Integration Technologies
- WSL2 networking and multi-vehicle simulation
- Mission Planner ground control integration
- MQTT broker with TLS security
- Hardware abstraction for SITL-to-deployment transition

## Running Projects

Please check individual README files for each project or your respective detailed Lab04 Notes.

## Deployment to Real Hardware

> **Warning** - Deployment Considerations: The codebase is designed for seamless transition from SITL to real hardware, though field deployment requires additional considerations for network reliability, power management, and environmental conditions.

### Connection String Changes
- **SITL**: `udp:127.0.0.1:14550`
- **Hardware**: `/dev/pixhawkN` (using udev rules for persistent device naming)

### udev Rules Setup
Create persistent device names for reliable hardware connections:
```bash
# Identify autopilot hardware
lsusb
udevadm info /dev/ttyACM0

# Create udev rule for consistent naming
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", SYMLINK+="pixhawk1"' | sudo tee /etc/udev/rules.d/99-autopilot.rules
```
**See detailed notes on this procedure in LAB04** <a href="https://docs.google.com/document/d/1SLUqKg_LtrjFXDIMmjbUGJ_1kaPP0MpPiJDBd1CsTGM/edit?tab=t.0#bookmark=id.fechda8p8tms" target="_blank">relevant notes</a>.

## Network Architecture

### SITL Environment
```
Python Scripts → Localhost UDP → SITL Instances
SITL Instances → Windows Host → Mission Planner
All Vessels → MQTT Broker → Inter-vessel Communication
```

### Features
- Independent programmatic control per vessel
- Unified ground control visualization
- Real-time inter-vessel coordination
- Scalable multi-vessel architecture

## Educational Value

This workshop provides hands-on experience with:
- **Modern Python development** practices and architecture
- **Autonomous systems programming** with industry-standard tools
- **Real-time communication** and coordination protocols
- **Professional deployment** patterns and hardware integration
- **Safety-critical systems** design and implementation

Perfect for undergraduate and graduate students in computer science, engineering, robotics, and maritime technology programs.

## Contributing

This repository represents a complete educational curriculum. Each project directory contains detailed technical documentation explaining implementation decisions and architectural choices.

## License

© 2025, Nikos Goulas, Thomas Kogias, Nikos Sapountzis - [SmartMove Lab](https://smartmove.aegean.gr), University of the Aegean

Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. You are free to share and adapt this material for non-commercial educational purposes with proper attribution.
