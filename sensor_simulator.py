import time
import json
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import datetime

# --- AWS IoT Core Configuration ---
# Replace with your actual values
AWS_IOT_ENDPOINT = "" # e.g., "xxxxx-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "MySimulatedDevice" # Must match the client ID allowed in your policy
PATH_TO_CERT = "" # e.g., "./xxxx-certificate.pem.crt"
PATH_TO_KEY = ""

    # e.g., "./xxxx-private.pem.key"
PATH_TO_ROOT_CA = "./AmazonRootCA1.pem"    # Path to the downloaded Amazon Root CA 1
TOPIC = "sensors/data"

# --- Sensor Simulation Parameters ---
SENSOR_TYPES = ["temperature", "humidity"] # Our two distinct sensors
DEVICE_ID = CLIENT_ID # Use the client ID as the device ID for simplicity
SEND_INTERVAL_SECONDS = 10 # Send data every 10 seconds (meets >= 15s requirement per sensor effectively)

# --- Initialize MQTT Client ---
myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myMQTTClient.configureEndpoint(AWS_IOT_ENDPOINT, 8883)
myMQTTClient.configureCredentials(PATH_TO_ROOT_CA, PATH_TO_KEY, PATH_TO_CERT)

# --- AWSIoTMQTTClient connection configuration ---
myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# --- Sensor State (Basic Simulation) ---
sensor_state = {
    "temperature": 20.0,
    "humidity": 50.0
}

def generate_sensor_data(sensor_type):
    """Generates slightly varying data based on sensor type."""
    current_value = sensor_state[sensor_type]
    if sensor_type == "temperature":
        # Simulate temperature drift +/- 0.5 degrees
        new_value = current_value + random.uniform(-0.5, 0.5)
        # Keep within a reasonable range (e.g., 0-40 C)
        new_value = max(0, min(40, new_value))
    elif sensor_type == "humidity":
        # Simulate humidity drift +/- 2%
        new_value = current_value + random.uniform(-2.0, 2.0)
        # Keep within 0-100%
        new_value = max(0, min(100, new_value))
    else:
         new_value = current_value # Default for unknown types

    sensor_state[sensor_type] = new_value # Update state for next reading
    return round(new_value, 2)

# --- Connect and Publish ---
print("Connecting to AWS IoT...")
myMQTTClient.connect()
print("Connected.")

try:
    while True:
        for sensor_type in SENSOR_TYPES:
            value = generate_sensor_data(sensor_type)
            timestamp_ms = int(time.time() * 1000) # Use epoch milliseconds

            message = {
                "deviceID": DEVICE_ID,
                "sensorType": sensor_type,
                "value": value,
                "timestamp": timestamp_ms,
                "datetime": datetime.datetime.utcfromtimestamp(timestamp_ms / 1000).isoformat() + "Z"
            }
            message_json = json.dumps(message)

            try:
                myMQTTClient.publish(TOPIC, message_json, 1) # QoS 1
                print(f"Published to {TOPIC}: {message_json}")
            except Exception as e:
                print(f"Error publishing: {e}")

            # Wait briefly between sensor types if desired, but the main wait is below
            # time.sleep(1)

        print(f"--- Waiting for {SEND_INTERVAL_SECONDS} seconds ---")
        time.sleep(SEND_INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("Disconnecting...")
    myMQTTClient.disconnect()
    print("Disconnected.")

except Exception as e:
    print(f"An error occurred: {e}")
    myMQTTClient.disconnect()