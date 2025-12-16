import os
import json
from flask import Flask, request, jsonify, send_from_directory
from azure.storage.blob import BlobServiceClient

# ---------------------------------------------------------
# CONFIGURE FLASK SO IT KNOWS WHERE STATIC FILES ARE
# ---------------------------------------------------------
app = Flask(__name__, static_folder="static", static_url_path="")

# ---------------------------------------------------------
# 1. LOAD AZURE STORAGE
# ---------------------------------------------------------
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not connect_str:
    print("ERROR: Azure Storage connection string not found!")
    print("Set AZURE_STORAGE_CONNECTION_STRING as an environment variable.")
else:
    print("Azure Storage connection string loaded.")

blob_service_client = BlobServiceClient.from_connection_string(connect_str)

container_name = "telemetry"
container_client = blob_service_client.get_container_client(container_name)

# ---------------------------------------------------------
# 2. DEVICES + CONFIG
# ---------------------------------------------------------
devices = [
    {"deviceId": "thermo-001", "location": "Living Room", "status": "online"},
    {"deviceId": "thermo-002", "location": "Bedroom", "status": "offline"}
]

configurations = {
    "thermo-001": {"targetTemperature": 22, "mode": "AUTO"},
    "thermo-002": {"targetTemperature": 20, "mode": "MANUAL"}
}

# ---------------------------------------------------------
# 3. FRONTEND ROUTE
# ---------------------------------------------------------
@app.route("/")
def dashboard():
    return send_from_directory(app.static_folder, "index.html")

# ---------------------------------------------------------
# 4. API ROUTES
# ---------------------------------------------------------
@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

@app.route("/devices/<deviceId>/telemetry", methods=["POST"])
def send_telemetry(deviceId):
    data = request.json
    blob_name = f"{deviceId}_latest.json"

    container_client.upload_blob(
        name=blob_name,
        data=json.dumps(data),
        overwrite=True
    )

    print(f"Saved telemetry for {deviceId} → {blob_name}")
    return {"status": "saved to blob storage"}, 200

@app.route("/devices/<deviceId>/telemetry", methods=["GET"])
def get_telemetry(deviceId):
    blob_name = f"{deviceId}_latest.json"
    blob_client = container_client.get_blob_client(blob_name)

    if not blob_client.exists():
        return {"error": "No telemetry found"}, 404

    blob_data = blob_client.download_blob().readall()
    telemetry = json.loads(blob_data)
    return jsonify(telemetry)

@app.route("/devices/<deviceId>/config", methods=["GET"])
def get_config(deviceId):
    return jsonify(configurations.get(deviceId, {}))

@app.route("/devices/<deviceId>/config", methods=["PUT"])
def update_config(deviceId):
    new_config = request.json
    configurations[deviceId] = new_config
    return {"status": "updated"}, 200

# ---------------------------------------------------------
# 5. RUN SERVER
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
