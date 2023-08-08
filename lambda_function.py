import json
from simulate import simulate, optimise

def lambda_handler(event, _context):
    params = default_params()

    match event.get("type"):
        case "simulate": 
            params["sessions"] = 2**16, # 262144
            results = simulate(params)["success_rate"]
        case "optimise":
            params["sessions"] = 2**13, # 8192
            results = optimise(params)
        case _: 
            results = {"error": "Invalid type"}


    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }


def default_params():
    return {
        "type": "simulate",
        "session_instance": None,
        "sim_data": {
            "strategy": "optimal_guetting",
            "bankroll": 50,
            "bet_unit": 2.5,
            "profit_goal": 100,
            "min_rounds": 0,
            "max_rounds": 0,
            "baccarat": False,
            "table_limits": 0
            },
        "optimise_data": {
            "optimise_bet": False,
            "min_win_chance": None
        }
    }

# Update default_params with the provided event data
def override_default(params, event):
    for key, value in event.items():
        if key == "data":
            params[key].update(value)
        else:
            params[key] = value