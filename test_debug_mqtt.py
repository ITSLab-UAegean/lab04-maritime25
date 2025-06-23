# test_mqtt_debug.py
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import time
import sys

print("=== MQTT Test Script Debug Version ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Check if .env file exists
env_file = ".env"
if os.path.exists(env_file):
    print(f"[OK] Found .env file at: {os.path.abspath(env_file)}")
    # Show file size for verification
    file_size = os.path.getsize(env_file)
    print(f"  .env file size: {file_size} bytes")
else:
    print(f"[ERROR] .env file not found at: {os.path.abspath(env_file)}")
    print("  Make sure the .env file exists in the same directory as this script")
    sys.exit(1)

# Load environment variables
print("\n--- Loading Environment Variables ---")
try:
    load_dotenv()
    print("[OK] dotenv.load_dotenv() completed")
except Exception as e:
    print(f"[ERROR] loading .env file: {e}")
    sys.exit(1)

# Check and display MQTT settings
print("\n--- Checking MQTT Configuration ---")
broker = os.getenv('MQTT_BROKER')
port_str = os.getenv('MQTT_PORT')
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')
use_tls = os.getenv('MQTT_USE_TLS', 'false').lower() == 'true'
ca_cert_path = os.getenv('MQTT_CA_CERT_PATH')

print(f"MQTT_BROKER: {broker if broker else 'NOT SET'}")
print(f"MQTT_PORT: {port_str if port_str else 'NOT SET'}")
print(f"MQTT_USERNAME: {username if username else 'NOT SET'}")
print(f"MQTT_PASSWORD: {'SET' if password else 'NOT SET'}")
print(f"MQTT_USE_TLS: {use_tls}")
print(f"MQTT_CA_CERT_PATH: {ca_cert_path if ca_cert_path else 'NOT SET'}")

# Validate all required variables are present
missing_vars = []
if not broker:
    missing_vars.append('MQTT_BROKER')
if not port_str:
    missing_vars.append('MQTT_PORT')
if not username:
    missing_vars.append('MQTT_USERNAME')
if not password:
    missing_vars.append('MQTT_PASSWORD')

# Check TLS-specific requirements
if use_tls and not ca_cert_path:
    missing_vars.append('MQTT_CA_CERT_PATH (required when MQTT_USE_TLS=true)')

if missing_vars:
    print(f"[ERROR] Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Convert port to integer
try:
    port = int(port_str)
    print(f"[OK] Port conversion successful: {port}")
except ValueError as e:
    print(f"[ERROR] Invalid port number '{port_str}': {e}")
    sys.exit(1)

# Check paho-mqtt version
try:
    print(f"[OK] paho-mqtt version: {mqtt.__version__}")
except AttributeError:
    print("[OK] paho-mqtt imported (version info not available)")

# Connection state tracking
connection_established = False
connection_error_code = None

# Callback functions with enhanced debugging
def on_connect(client, userdata, flags, rc):
    global connection_established, connection_error_code
    print(f"\n--- on_connect callback triggered ---")
    print(f"  Result code: {rc}")
    print(f"  Flags: {flags}")
    
    if rc == 0:
        print(f"[OK] Connected successfully to {broker}:{port}")
        connection_established = True
        
        # Subscribe to test topic
        try:
            result, mid = client.subscribe("test/lab04")
            print(f"[OK] Subscribe request sent - Result: {result}, Message ID: {mid}")
        except Exception as e:
            print(f"[ERROR] during subscribe: {e}")
    else:
        connection_established = False
        connection_error_code = rc
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorized"
        }
        error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
        print(f"[ERROR] Connection failed: {error_msg}")

def on_message(client, userdata, msg):
    print(f"\n--- Message received ---")
    print(f"  Topic: {msg.topic}")
    print(f"  Payload: {msg.payload.decode()}")
    print(f"  QoS: {msg.qos}")
    print(f"  Retain: {msg.retain}")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"[OK] Subscription confirmed - Message ID: {mid}, QoS: {granted_qos}")

def on_publish(client, userdata, mid):
    print(f"[OK] Publish confirmed - Message ID: {mid}")

def on_disconnect(client, userdata, rc):
    print(f"\n--- Disconnection event ---")
    if rc != 0:
        print(f"[ERROR] Unexpected disconnection - Result code: {rc}")
    else:
        print("[OK] Clean disconnection")

def on_log(client, userdata, level, buf):
    print(f"[MQTT LOG] {buf}")

# Create MQTT client with enhanced debugging
print("\n--- Creating MQTT Client ---")
try:
    client = mqtt.Client()
    print("[OK] MQTT client created successfully")
except Exception as e:
    print(f"[ERROR] creating MQTT client: {e}")
    sys.exit(1)

# Set up all callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_publish = on_publish
client.on_disconnect = on_disconnect
client.on_log = on_log  # Enable detailed logging

# Configure SSL/TLS based on environment variables
print("\n--- Checking SSL/TLS Configuration ---")
if use_tls:
    print("MQTT_USE_TLS=true - enabling SSL/TLS")
    
    # Check if CA certificate file exists
    if ca_cert_path and os.path.exists(ca_cert_path):
        print(f"[OK] Found CA certificate file: {os.path.abspath(ca_cert_path)}")
        ca_file_size = os.path.getsize(ca_cert_path)
        print(f"  CA cert file size: {ca_file_size} bytes")
        
        # Try to examine the certificate file
        try:
            with open(ca_cert_path, 'r') as f:
                cert_content = f.read()
                cert_count = cert_content.count('-----BEGIN CERTIFICATE-----')
                print(f"  Certificates in file: {cert_count}")
                if cert_count == 0:
                    print("  [WARNING] No certificates found in file!")
                elif cert_count == 1:
                    print("  [INFO] Single certificate (may need full chain)")
                else:
                    print("  [INFO] Multiple certificates (certificate chain)")
        except Exception as e:
            print(f"  [WARNING] Could not examine certificate file: {e}")
    elif ca_cert_path:
        print(f"[ERROR] CA certificate file not found: {os.path.abspath(ca_cert_path)}")
        sys.exit(1)
    else:
        print("[WARNING] No CA certificate path specified, will use system default")
        ca_cert_path = None
    
    try:
        import ssl
        
        # Prefer the provided CA certificate file for maximum compatibility
        if ca_cert_path and os.path.exists(ca_cert_path):
            print(f"[INFO] Using provided CA certificate file: {ca_cert_path}")
            client.tls_set(ca_certs=ca_cert_path, certfile=None, keyfile=None, 
                          cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS,
                          ciphers=None)
            print("[OK] SSL/TLS enabled with provided CA certificate")
        else:
            # Fallback to system default CAs (includes Let's Encrypt)
            print("[INFO] No CA cert file found, using system default CA certificates")
            ctx = ssl.create_default_context()
            client.tls_set_context(ctx)
            print("[OK] SSL/TLS enabled using system default CA certificates")
            
    except Exception as e:
        print(f"[ERROR] configuring SSL/TLS: {e}")
        
        # Final fallback: try with relaxed verification for debugging
        print("\n[ATTEMPTING] Final fallback with relaxed certificate verification...")
        try:
            client.tls_set(ca_certs=None, certfile=None, keyfile=None, 
                          cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS,
                          ciphers=None)
            client.tls_insecure_set(True)
            print("[OK] SSL/TLS enabled with relaxed verification (development mode)")
            print("      WARNING: This disables certificate validation!")
        except Exception as e2:
            print(f"[ERROR] even relaxed SSL/TLS failed: {e2}")
            sys.exit(1)
else:
    print("MQTT_USE_TLS=false - using plain text connection")

# Set username and password
print("\n--- Setting Authentication ---")
try:
    client.username_pw_set(username, password)
    print("[OK] Username and password set")
except Exception as e:
    print(f"[ERROR] setting credentials: {e}")
    sys.exit(1)

# Attempt connection
print(f"\n--- Attempting Connection ---")
print(f"Connecting to {broker}:{port} as {username}...")
try:
    result = client.connect(broker, port, 60)
    print(f"[OK] Connect method called - Result: {result}")
except Exception as e:
    print(f"[ERROR] during connection attempt: {e}")
    sys.exit(1)

# Start the network loop
print("\n--- Starting Network Loop ---")
try:
    client.loop_start()
    print("[OK] Network loop started")
except Exception as e:
    print(f"[ERROR] starting network loop: {e}")
    sys.exit(1)

# Wait for connection with timeout
print("\n--- Waiting for Connection ---")
timeout = 10  # seconds
start_time = time.time()
while not connection_established and (time.time() - start_time) < timeout:
    if connection_error_code is not None:
        break
    time.sleep(0.1)

if not connection_established:
    if connection_error_code is not None:
        print(f"[ERROR] Connection failed with error code: {connection_error_code}")
    else:
        print(f"[ERROR] Connection timeout after {timeout} seconds")
    client.loop_stop()
    sys.exit(1)

print("[OK] Connection established, proceeding with test messages...")

# Publish test messages
print("\n--- Publishing Test Messages ---")
for i in range(3):
    message = f"Test message {i+1} from Lab04"
    try:
        result = client.publish("test/lab04", message)
        print(f"[OK] Published message {i+1} - Result: {result.rc}, Message ID: {result.mid}")
        print(f"  Content: {message}")
    except Exception as e:
        print(f"[ERROR] publishing message {i+1}: {e}")
    
    time.sleep(1)

# Keep running to receive messages
print("\n--- Waiting for Messages ---")
print("Listening for 5 seconds...")
time.sleep(5)

# Clean shutdown
print("\n--- Cleaning Up ---")
try:
    client.loop_stop()
    print("[OK] Network loop stopped")
except Exception as e:
    print(f"[ERROR] stopping loop: {e}")

try:
    client.disconnect()
    print("[OK] Disconnected from broker")
except Exception as e:
    print(f"[ERROR] during disconnect: {e}")

print("\n=== Script completed ===")