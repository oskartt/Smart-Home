# Smart-Home

Repository for our IoT group: 
Smart Thermostat IoT System:

An intelligent home thermostat that automatically increases its heating level when it’s cold outside and decreases it when it’s warm, maintaining comfort and optimizing energy use. 

Members:
- Mehmet Ali Kurnaz,  
- Efe Demir,  
- Oskar Przybyl,  
- Yardiel Omar Lopez Estevez.



---

## Overview

The Smart Thermostat is an IoT-based system that adapts to outdoor temperature changes.  
It connects to the internet, reads real-time weather data (or sensor data), and adjusts heating or cooling using a simple level-based logic.

When it’s cold, the thermostat **levels up** to increase indoor temperature.  
When it’s warm, it **levels down** to save energy.

## Data Storage Infrastructure

Azure Blob Storage is used as the data storage solution for the Smart Thermostat system.

The storage account stores:
- Device telemetry data
- Temperature history
- System logs

The infrastructure was created using Microsoft Azure and exported as an ARM template.
The template files are located in:
- infrastructure/blob-storage/

This allows the storage infrastructure to be recreated automatically.


## REST API Documentation

The Smart Thermostat REST API is documented using Swagger (OpenAPI).

The API specification is available in this repository:
- `openapi-unresolved.yaml`

The API defines endpoints for:
- Retrieving registered devices
- Sending telemetry data from thermostats
- Reading and updating thermostat configuration
