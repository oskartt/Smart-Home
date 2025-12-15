from dotenv import load_dotenv
load_dotenv()
import random
import time
import json
import os
from datetime import datetime
from paho.mqtt import client as mqtt
from azure.storage.blob import BlobServiceClient

# -------------------------------
#  AZURE STORAGE CONFIG
# -------------------------------

# Load connection string from environment (App Service or local .env)
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
API_URL = "https://thermostatproject-bndcdmebfqbteagf.switzerlandnorth-01.azurewebsites.net/devices/thermo-001/telemetry"

# Create client for Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# CHANGE this to your real container name (Azure → Storage Account → Containers)
container_name = "telemetry"
container_client = blob_service_client.get_container_client("telemetry")

# -------------------------------
#  MQTT CONFIG
# -------------------------------

device_id = "Thermostat_device_01"
mqtt_hub_hostname = "172.161.150.169"
mqtt_hub_port = 1883

# Topics
publish_topic = f"devices/{device_id}/messages/events/"
command_topic = f"devices/{device_id}/commands"

# -------------------------------
#  CALLBACK FUNCTIONS
# -------------------------------

def on_connect(client, userdata, flags, rc):
    print(f"Device connected with result code: {rc}")
    client.subscribe(command_topic)

def on_disconnect(client, userdata, rc):
    print(f"Device disconnected with result code: {rc}")

def on_publish(client, userdata, mid):
    print("Device sent message")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed to topic '{command_topic}'")

def on_message(client, userdata, msg):
    global target_temperature
    print(f"Received message: {msg.payload.decode()}")
    try:
        payload = json.loads(msg.payload)
        if "target_temperature" in payload:
            target_temperature = float(payload["target_temperature"])
            print(f"Target temperature updated to {target_temperature}")
    except Exception as e:
        print(f"Failed to process command: {e}")

# -------------------------------
#  THERMOSTAT SIMULATION LOGIC
# -------------------------------

target_temperature = 24.0
current_temperature = 20.0
outside_temperature = 15.0
tolerance = 0.5
humidity = 50.0
pressure = 1012.0

# -------------------------------
#  MQTT INIT
# -------------------------------

client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message

print("Connecting to MQTT broker...")
client.connect(mqtt_hub_hostname, mqtt_hub_port)
client.loop_start()

print(f"Connected. Publishing to topic: {publish_topic}")

# -------------------------------
#  MAIN LOOP
# -------------------------------
while True:
    heating_on = False
    cooling_on = False

    if current_temperature < target_temperature - tolerance:
        heating_on = True
        current_temperature += 0.5
    elif current_temperature > target_temperature + tolerance:
        cooling_on = True
        current_temperature -= 0.5
    else:
        current_temperature += (outside_temperature - current_temperature) * 0.1

    humidity += random.uniform(-0.5, 0.5)
    humidity = max(20.0, min(80.0, humidity))

    pressure += random.uniform(-1, 1)
    pressure = max(900.0, min(1100.0, pressure))

    # Telemetry payload
    payload = {
        "device_id": device_id,
        "current_temperature": round(current_temperature, 2),
        "target_temperature": target_temperature,
        "humidity": round(humidity, 2),
        "pressure": round(pressure, 2),
        "heating_on": heating_on,
        "cooling_on": cooling_on,
        "timestamp": time.time()
    }

    message = json.dumps(payload)

    # -------------------------------
    #  MQTT PUBLISH
    # -------------------------------
    client.publish(publish_topic, message, qos=1)
    print(f"MQTT message sent: {message}")

    # -------------------------------
    #  SAVE TO AZURE BLOB STORAGE
    # -------------------------------
    blob_name = f"{device_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    container_client.upload_blob(
        name=blob_name,
        data=message,
        overwrite=True
    )
    print(f"Saved telemetry to Azure Blob: {blob_name}")

    time.sleep(5)
