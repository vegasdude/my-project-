import json
import math
import sys

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def haversine(a, b):
    # distance (meters)
    R = 6371000
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))

def violates_zone(point, zone):
    return haversine(point, zone["center"]) <= zone["radius_meters"]

def evaluate(plan, rules):
    violations = []

    if plan["max_altitude"] > rules["max_altitude_meters"]:
        violations.append("Altitude exceeds limit")

    if plan["max_speed"] > rules["max_speed_mps"]:
        violations.append("Speed exceeds limit")

    for p in plan["path"]:
        for z in rules["no_fly_zones"]:
            if violates_zone(p, z):
                violations.append(f"Path enters no-fly zone: {z['name']}")

    if rules.get("require_logging") and not plan.get("logging_enabled"):
        violations.append("Logging required but not enabled")

    return violations

if __name__ == "__main__":
    plan = load_json(sys.argv[1])
    rules = load_json("policy/rules.json")

    v = evaluate(plan, rules)

    if not v:
        print("Flight plan approved ✔")
    else:
        print("Flight plan rejected ❌")
        for x in v:
            print("•", x)