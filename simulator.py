import random
import time
import json
from paho.mqtt import client as mqtt

# MQTT broker details (Docker Mosquitto)
device_id = "Thermostat_device_01"
mqtt_hub_hostname = "172.161.150.169"
mqtt_hub_port = 1883

# Thermostat parameters
target_temperature = 24.0        # Desired room temperature
current_temperature = 20.0       # Initial room temperature
outside_temperature = 15.0       # Simulated outside temperature
tolerance = 0.5                  # Temperature tolerance for switching heating/cooling
humidity = 50.0                   # Initial humidity
pressure = 1012.0                 # Initial pressure

# MQTT topic
publish_topic = f"devices/{device_id}/messages/events/"
command_topic = f"devices/{device_id}/commands"

# Callback functions
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

# Initialize MQTT client
client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message

print("Connecting to MQTT broker...")
client.connect(mqtt_hub_hostname, mqtt_hub_port)
client.loop_start()  # Start background thread for MQTT

print(f"Connected. Publishing to topic: {publish_topic}")

# Main loop: simulate thermostat
while True:
    # Heating/cooling logic
    heating_on = False
    cooling_on = False

    if current_temperature < target_temperature - tolerance:
        heating_on = True
    elif current_temperature > target_temperature + tolerance:
        cooling_on = True

    # Update current_temperature gradually
    if heating_on:
        current_temperature += 0.5
    elif cooling_on:
        current_temperature -= 0.5
    else:
        # Move slowly toward outside temperature
        current_temperature += (outside_temperature - current_temperature) * 0.1

    # Simulate small humidity and pressure variations
    humidity += random.uniform(-0.5, 0.5)
    humidity = max(20.0, min(80.0, humidity))  # clamp to realistic values
    pressure += random.uniform(-1, 1)
    pressure = max(900.0, min(1100.0, pressure))

    # Prepare payload
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
    client.publish(publish_topic, message, qos=1)
    print(f"Message sent: {message}")

    time.sleep(5)  # wait 5 seconds before next reading
