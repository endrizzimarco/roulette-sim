from simulate import simulate, optimise, CasinoSession
import pickle
import json
import base64
import time

def lambda_handler(event, _context):
    event = event.get('queryStringParameters') or event 
    params = override_default(default_params(), event)

    match params.get("type"):
        case "get_strategies":
            results =  list(CasinoSession().strategies.keys())
        case "simulate": 
            if not params.get('session_instance'): 
                session = CasinoSession(**params["data"])
            else: 
                # Decode the base64-encoded string to bytes and unpickle
                decoded_state = base64.b64decode(params['session_instance'])
                session = pickle.loads(decoded_state)

            session = session.tick(win=int(params['won']))
            time1 = time.time()
            chance = simulate(params, session)["success_rate"]
            time2 = time.time()

            params["sessions"] = 2**15 # 32768
            results = {
                "data": {
                    "chance": chance,
                    "bankroll": session.bankroll,
                    "next_bet": session.curr_bet,
                    "round": session.round,
                    "time": time2-time1
                }, 
                "state": base64.b64encode(pickle.dumps(session)).decode('utf-8')  # Encode to base64
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