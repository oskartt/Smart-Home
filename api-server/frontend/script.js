const API_URL = "https://thermostatproject-bndcdmebfqbteagf.switzerlandnorth-01.azurewebsites.net/devices/thermo-001/telemetry";

async function loadData() {
    try {
        const res = await fetch(API_URL);
        const data = await res.json();

        document.getElementById("temp").innerText   = data.current_temperature;
        document.getElementById("target").innerText = data.target_temperature;
        document.getElementById("hum").innerText    = data.humidity;
        document.getElementById("press").innerText  = data.pressure;
        document.getElementById("heat").innerText   = data.heating_on ? "ON" : "OFF";
        document.getElementById("cool").innerText   = data.cooling_on ? "ON" : "OFF";
    }
    catch (err) {
        console.error("Error loading telemetry:", err);
    }
}

setInterval(loadData, 3000);  // refresh every 3 seconds
loadData();
