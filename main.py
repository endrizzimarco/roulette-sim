from prettytable import PrettyTable
import matplotlib.pyplot as plt
from strategies import Strategy
from statistics import median
import seaborn as sns

sessions = 2**12# 4096
strat = "optimal_guetting"
bankroll = 50
bet = 2.5
profit_goal = 100
min_rounds = 0
max_rounds = 0
baccarat = False

def plot_bankroll_and_bet(data):
  sns.set_style("darkgrid")
  plt.ylabel("Amount (£)")
  plt.xlabel("Rounds")
  plt.title(f"Bankroll and Bet over time for final session ({strat})")
  plt.plot(data["bankroll"][-1], label ="Bankroll")
  plt.plot(data["bets"][-1], label="Bet")
  plt.legend()
  plt.show()

def simulate(sessions=sessions, strat=strat, bankroll=bankroll, bet=bet, profit_goal=profit_goal, min_rounds=min_rounds, max_rounds=max_rounds, baccarat=baccarat):
  reached_profit_goal = 0
  bankroll_histories = []
  bets_histories = []
  for _ in range(sessions):
    strategy = Strategy(bankroll, bet, profit_goal, min_rounds, max_rounds, baccarat=baccarat)
    results = strategy.execute(strat)
    bankroll_histories.append(results["bankroll"])
    bets_histories.append(results["bets"])

  # print(bankroll_histories[-1])
  total_rounds = [len(session) for session in bankroll_histories]
  average_rounds = sum(total_rounds) / len(total_rounds)
  median_rounds = median(total_rounds)
  winning_rounds = [len(session) for session in bankroll_histories if session[-1] >= profit_goal]
  average_winning_rounds = sum(winning_rounds) / len(winning_rounds) if len(winning_rounds) > 0 else 0
  losing_rounds = [len(session) for session in bankroll_histories if session[-1] <= 0]
  average_losing_rounds = sum(losing_rounds) / len(losing_rounds) if len(losing_rounds) > 0 else 0

  reached_profit_goal = [session for session in bankroll_histories if session[-1] >= profit_goal]
  success_rate = len(reached_profit_goal)/sessions * 100
  reached_close_profit_goal = [session for session in bankroll_histories if any(bankroll >= profit_goal*0.75 for bankroll in session)]
  close_success_rate = len(reached_close_profit_goal)/sessions * 100

  average_bankroll_after_10_rounds = sum([session[10] if len(session) > 10 else 0 for session in bankroll_histories]) / len(bankroll_histories)
  average_final_bankroll = sum([session[-1] for session in bankroll_histories]) / len(bankroll_histories)

  stats_table = PrettyTable(["Session aim", "3/4 session aim", "Avg rounds", "Median rounds", "Avg W rounds", "Avg L rounds", "Avg @ 10 rounds", "House edge"])
  stats_table.add_row([f"{success_rate:.2f}%", 
                       f"{close_success_rate:.2f}%", 
                       f"{average_rounds:.2f}", 
                       median_rounds, 
                       f"{average_winning_rounds:.2f}",
                       f"{average_losing_rounds:.2f}",
                       f"£{average_bankroll_after_10_rounds:.2f}", 
                       f"{(bankroll - average_final_bankroll)/bankroll * 100:.2f}%"])
  
  print(bankroll_histories[-1])
  return {"bankroll": bankroll_histories, "bets": bets_histories, "success_rate": success_rate, "stats_table": stats_table}

def print_stats_table(data):
  print(f"\nstrat: {strat}, bankroll: £{bankroll}, bet: £{bet}, session aim: £{profit_goal}")
  print(data["stats_table"])

def find_optimal_bet_size(strat):
  bets_range = [i * 0.5 for i in range(1, int(bankroll/2))]
  best_bet = 0
  best_chance = 0
  for bet in bets_range:
    chance = simulate(strat=strat, bet=bet)["success_rate"]
    if chance > best_chance: 
      best_bet = bet 
      best_chance = chance
      # print(f"({strat}) New best bet: {best_bet}, with chance {chance}%")
  return (best_bet, best_chance)

def optimise(optimise_bet=False, win_chance=0, min_rounds=0, max_rounds=0):
  strategies = []
  bets = []
  chances = []

  for strategy in Strategy().strategies.keys():
    chance = simulate(strat=strategy, min_rounds=min_rounds, max_rounds=max_rounds)["success_rate"]
    if optimise_bet: 
      bet, chance = find_optimal_bet_size(strategy)
    if win_chance and chance <= win_chance:
      continue
    strategies.append(strategy)
    chances.append(chance)
    bets.append(bet if optimise_bet else bets)

  if win_chance and not chances: 
    global profit_goal
    profit_goal -= 0.1 * profit_goal
    print(f"changing session aim to: {profit_goal}")
    optimise(optimise_bet, win_chance, max_rounds)
    
  if optimise_bet: 
    result = sorted(zip(strategies, bets, chances), key=lambda x: x[2], reverse=True)
  else:
    result = sorted(zip(strategies, chances), key=lambda x: x[1], reverse=True)
    
  return result[:3]


if __name__ == "__main__":
  data = simulate()
  print_stats_table(data)
  # plot_bankroll_and_bet(data)
  print(optimise(optimise_bet=False))

