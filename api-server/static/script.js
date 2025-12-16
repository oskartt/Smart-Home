async function fetchTelemetry() {
    try {
        const response = await fetch("/devices/thermo-001/telemetry");
        if (!response.ok) {
            console.log("No telemetry yet");
            return;
        }

        const data = await response.json();

        document.getElementById("temp").textContent = data.temperature ?? "--";
        document.getElementById("target").textContent = data.targetTemperature ?? "--";
        document.getElementById("hum").textContent = data.humidity ?? "--";
        document.getElementById("press").textContent = data.pressure ?? "--";
        document.getElementById("heat").textContent = data.heating ? "ON" : "OFF";
        document.getElementById("cool").textContent = data.cooling ? "ON" : "OFF";

    } catch (err) {
        console.error("Error fetching telemetry:", err);
    }
}

// Update telemetry every 2 seconds
setInterval(fetchTelemetry, 2000);

// Load immediately
fetchTelemetry();
