from strategies import Strategy


def simulate(params):
  reached_profit_goal = 0
  bankroll_histories = []
  bets_histories = []
  for _ in range(params["sessions"]):
    results = Strategy(**params["data"]).execute(params["strat"])
    bankroll_histories.append(results["bankroll"])
    if results["bankroll"][-1] >= params["data"]["profit_goal"]: reached_profit_goal += 1
    bets_histories.append(results["bets"])
  success_rate = reached_profit_goal/params["sessions"] * 100
  
  return {"bankroll_histories": bankroll_histories, "bets_histories": bets_histories, "success_rate": success_rate}

def find_optimal_bet_size(params):
  best_bet = 0
  best_chance = 0
  bankroll = params["data"]["bankroll"]
  for bet in range(int(bankroll/4), int(bankroll/2)): #FIXME: this is shit!
    params["data"]["bet"] = bet
    chance = simulate(params)["success_rate"]
    if chance > best_chance: 
      best_bet = bet 
      best_chance = chance
      # print(f"({strat}) New best bet: {best_bet}, with chance {chance}%")
  return (best_bet, best_chance)

def optimise(params, optimise_bet=False, win_chance=0):
  strategies = []
  chances = []
  bets = []

  for strategy in Strategy().strategies.keys():
    params["strat"] = strategy
    chance = simulate(params)["success_rate"]
    if optimise_bet: 
      bet, chance = find_optimal_bet_size(params)
    if win_chance and chance <= win_chance:
      continue
    strategies.append(strategy)
    chances.append(chance)
    if optimise_bet: bets.append(bet)

  if win_chance and not chances: 
    params["data"]["profit_goal"] -= params["data"]["profit_goal"] * 0.1
    print(f"changing session aim to: {params['data']['profit_goal']}")
    return optimise(params, optimise_bet=optimise_bet, win_chance=win_chance)

  if optimise_bet: 
    result = sorted(zip(strategies, bets, chances), key=lambda x: x[2], reverse=True)
  else:
    result = sorted(zip(strategies, chances), key=lambda x: x[1], reverse=True)
    
  return result[:5] if not win_chance else (params["data"]["profit_goal"], result[:5])