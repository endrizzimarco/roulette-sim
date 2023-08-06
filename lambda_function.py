import json
from simulate import simulate, optimise

def lambda_handler(event, _context):
    params = {
    "sessions": 2**18, # 262144
    "strat": "optimal_guetting",
    "data": {
        "bankroll": 50,
        "bet": 2.5,
        "profit_goal": 100,
        "min_rounds": 0,
        "max_rounds": 0,
        "baccarat": False
        },
    # optimise params
    "optimise_bet": False,
    "win_chance": None
    }

    # Update default_params with the provided event data
    for key, value in event.items():
        if key == "data":
            params[key].update(value)
        else:
            params[key] = value

    if event.get("optimise"):
        results = optimise(params)
    else:
        results = simulate(params, parallelise=False)["success_rate"]


    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
