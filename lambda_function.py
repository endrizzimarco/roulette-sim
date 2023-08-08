from simulate import simulate, optimise, CasinoSession
import pickle
import json

def lambda_handler(event, _context):
    params = override_default(default_params(), event)

    match event.get("type"):
        case "simulate": 
            if not params.get('session_instance'): 
                session = CasinoSession(**params["data"])
            else: 
                session = pickle.loads(params["session_instance"])
            state = session.tick()
            results = pickle.dumps(state)

            params["sessions"] = 2**16, # 262144
            results = simulate(params)["success_rate"]
        case "optimise":
            params["sessions"] = 2**13, # 8192
            results = optimise(params)
        case _: 
            return {
                'statusCode': 400,
                'body': {"error": "Invalid type"}
            }
        

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }


def default_params():
    return {
        "type": "simulate",
        "session_instance": None,
        "won": False,
        "data": {
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
    return params