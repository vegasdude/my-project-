import json
import math
import sys
from datetime import datetime
from copy import deepcopy

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def haversine(a, b):
    R = 6371000
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))

def violates_airspace(point, airspace):
    hits = []
    for zone in airspace["airspace_classes"]:
        dist = haversine(point, zone["center"])
        if dist <= zone["radius_meters"]:
            hits.append(zone)
    return hits

def evaluate(plan, rules, airspace):
    violations = []

    if plan["max_altitude"] > rules["max_altitude_meters"]:
        violations.append("Altitude exceeds limit")

    if plan["max_speed"] > rules["max_speed_mps"]:
        violations.append("Speed exceeds limit")

    # No-fly zones
    for p in plan["path"]:
        for z in rules["no_fly_zones"]:
            if haversine(p, z["center"]) <= z["radius_meters"]:
                violations.append(f"Path enters no-fly zone: {z['name']}")

    # Airspace overlays
    for p in plan["path"]:
        matches = violates_airspace(p, airspace)

        for zone in matches:
            if zone.get("restricted"):
                violations.append(f"Restricted Airspace: {zone['name']}")

            if plan["max_altitude"] > zone.get("max_altitude_meters", 999999):
                violations.append(
                    f"Altitude violates {zone['class']} ceiling in {zone['name']}"
                )

    if rules.get("require_logging") and not plan.get("logging_enabled"):
        violations.append("Logging required but not enabled")

    return violations

def append_audit_record(plan, violations):
    log = load_json("policy/audit_log.json")

    log.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "flight_id": plan["flight_id"],
        "result": "APPROVED" if not violations else "REJECTED",
        "violations": violations
    })

    save_json("policy/audit_log.json", log)


def get_current_rule_version():
    history = load_json("policy/rules_history.json")
    return history[-1]["version"]

if __name__ == "__main__":
    plan = load_json(sys.argv[1])
    rules = load_json("policy/rules.json")
    airspace = load_json("policy/airspace.json")

    violations = evaluate(plan, rules, airspace)

    append_audit_record(plan, violations)

    print("Rule Version:", get_current_rule_version())

    if not violations:
        print("Flight plan approved ✔")
    else:
        print("Flight plan rejected ❌")
        for x in violations:
            print("•", x)