import os
import json
from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

# -------------------------------
# 1. LOAD AZURE STORAGE
# -------------------------------
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not connect_str:
    print("ERROR: Azure Storage connection string not found!")
    print("Set AZURE_STORAGE_CONNECTION_STRING as an environment variable.")
else:
    print("Azure Storage connection string loaded.")

# Connect to Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# IMPORTANT — CHANGE THIS TO YOUR REAL CONTAINER NAME
container_name = "telemetry"
container_client = blob_service_client.get_container_client(container_name)

# -------------------------------
# 2. IN-MEMORY DEVICES + CONFIG
# -------------------------------
devices = [
    {"deviceId": "thermo-001", "location": "Living Room", "status": "online"},
    {"deviceId": "thermo-002", "location": "Bedroom", "status": "offline"}
]

configurations = {
    "thermo-001": {"targetTemperature": 22, "mode": "AUTO"},
    "thermo-002": {"targetTemperature": 20, "mode": "MANUAL"}
}

# -------------------------------
# API ROUTES
# -------------------------------

@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

# -------------------------------------
# SAVE TELEMETRY INTO AZURE STORAGE
# -------------------------------------
@app.route("/devices/<deviceId>/telemetry", methods=["POST"])
def send_telemetry(deviceId):
    data = request.json

    # filename for blob
    blob_name = f"{deviceId}_latest.json"

    # Upload telemetry to Azure Blob Storage
    container_client.upload_blob(
        name=blob_name,
        data=json.dumps(data),
        overwrite=True
    )

    print(f"Saved telemetry for {deviceId} → {blob_name}")

    return {"status": "saved to blob storage"}, 200


# -------------------------------------
# READ TELEMETRY BACK FROM STORAGE
# -------------------------------------
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


# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
