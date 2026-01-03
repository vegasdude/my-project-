# Drone Policy

This project defines a simple policy engine for drone flight operations.  
You can configure rules (e.g., altitude limits, no-fly zones, speed limits) and evaluate flight plans for compliance.

## Features
- JSON-defined rules
- Policy validator
- Simple Python API
- Extensible

## Use Cases
✔ Research  
✔ Hobby drones  
✔ Prototyping policy systems

## Requirements
Python 3.9+

## Run Example
```bash
python policy/evaluator.py examples/sample_flight_plan.json