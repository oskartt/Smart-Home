let currentTarget = null;

// Fetch telemetry from API
async function fetchTelemetry() {
    try {
        const response = await fetch("/devices/thermo-001/telemetry");
        if (!response.ok) return;

        const data = await response.json();

        document.getElementById("temp").textContent = data.temperature ?? "--";
        document.getElementById("hum").textContent = data.humidity ?? "--";
        document.getElementById("press").textContent = data.pressure ?? "--";
        document.getElementById("heat").textContent = data.heating ? "ON" : "OFF";
        document.getElementById("cool").textContent = data.cooling ? "ON" : "OFF";

        // Save + display target temp
        currentTarget = data.targetTemperature ?? 20;
        document.getElementById("target").textContent = currentTarget;
        document.getElementById("adjustValue").textContent = currentTarget;

    } catch (err) {
        console.error("Telemetry error:", err);
    }
}

// Send updated target temperature
async function updateTargetTemperature(newTemp) {
    currentTarget = newTemp;

    // Update display
    document.getElementById("adjustValue").textContent = newTemp;
    document.getElementById("target").textContent = newTemp;

    // Send to backend
    await fetch("/devices/thermo-001/config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ targetTemperature: newTemp })
    });
}

// Button events
document.getElementById("minusBtn").onclick = () => {
    if (currentTarget !== null) updateTargetTemperature(currentTarget - 1);
};

document.getElementById("plusBtn").onclick = () => {
    if (currentTarget !== null) updateTargetTemperature(currentTarget + 1);
};

// Refresh telemetry every 2 seconds
setInterval(fetchTelemetry, 2000);
fetchTelemetry();
