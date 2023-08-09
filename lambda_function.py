from simulate import simulate, optimise, CasinoSession
import pickle
import json
import base64

def lambda_handler(event, _context):
    params = override_default(default_params(), event)

    match params.get("type"):
        case "simulate": 
            if not params.get('session_instance'): 
                session = CasinoSession(**params["data"])
            else: 
                # Decode the base64-encoded string to bytes
                decoded_state = base64.b64decode(params['session_instance'])
                
                # Unpickle the decoded bytes
                session = pickle.loads(decoded_state)

            state = session.tick()

            params["sessions"] = 2**15 # 32768
            results = {
                "chance": simulate(params)["success_rate"],
                "data": {
                    "bankroll": session.bankroll,
                    "last_bet": session.curr_bet,
                    "round": session.round,
                }, 
                "state": base64.b64encode(pickle.dumps(state)).decode('utf-8')  # Encode to base64
            }
        case "optimise":
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
        "sessions": 2**13,
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
            params[key].update(json.loads(value))
        else:
            params[key] = value
    return params