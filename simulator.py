import requests
import random
import time

API_BASE = "https://thermostatproject-bndcdmebfqbteagf.switzerlandnorth-01.azurewebsites.net"

# two devices
DEVICES = ["thermo-001", "thermo-002"]

# starting values
current_temp = {
    "thermo-001": 20,
    "thermo-002": 18
}

target_temp = {
    "thermo-001": 21,
    "thermo-002": 20
}

humidity = {
    "thermo-001": 40,
    "thermo-002": 45
}

pressure = {
    "thermo-001": 1012,
    "thermo-002": 1014
}

def simulate(device_id):
    global current_temp, target_temp, humidity, pressure

    # simple heating/cooling logic
    heating = False
    cooling = False

    if current_temp[device_id] < target_temp[device_id] - 0.5:
        heating = True
        current_temp[device_id] += 0.4
    elif current_temp[device_id] > target_temp[device_id] + 0.5:
        cooling = True
        current_temp[device_id] -= 0.4

    # small variation
    humidity[device_id] += random.uniform(-0.4, 0.4)
    pressure[device_id] += random.uniform(-1, 1)

    telemetry = {
        "temperature": round(current_temp[device_id], 2),
        "humidity": round(humidity[device_id], 2),
        "pressure": round(pressure[device_id], 2),
        "heating": heating,
        "cooling": cooling,
        "targetTemperature": target_temp[device_id]
    }

    url = f"{API_BASE}/devices/{device_id}/telemetry"
    response = requests.post(url, json=telemetry)

    print(device_id, telemetry, "→", response.status_code)


# continuous loop
while True:
    for dev in DEVICES:
        simulate(dev)
    time.sleep(5)
