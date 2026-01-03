from policy.evaluator import evaluate

def test_allowed():
    rules = {
        "max_altitude_meters": 120,
        "max_speed_mps": 15,
        "no_fly_zones": [],
        "require_logging": True
    }

    plan = {
        "max_altitude": 80,
        "max_speed": 10,
        "path": [],
        "logging_enabled": True
    }

    assert evaluate(plan, rules) == []