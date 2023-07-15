from strategies import Strategy
from statistics import median
import seaborn as sns
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import numpy as np

sessions = 2**12 # 4096
strat = "martingale"
bankroll = 50
bet = 2.5
session_aim = 100
max_rounds = 0

def plot_bankroll_and_bet(data):
  sns.set_style("darkgrid")
  plt.ylabel("Amount (£)")
  plt.xlabel("Rounds")
  plt.title(f"Bankroll and Bet over time for final session ({strat})")
  plt.plot(data["bankroll_histories"][-1], label ="Bankroll")
  plt.plot(data["bets_histories"][-1], label="Bet")
  plt.legend()
  plt.show()

def simulate(sessions=sessions, strat=strat, bankroll=bankroll, bet=bet, session_aim=session_aim, max_rounds=max_rounds):
  reached_session_aim = 0
  bankroll_histories = []
  bets_histories = []
  for _ in range(sessions):
    strategy = Strategy(bankroll, bet, session_aim, max_rounds)
    results = strategy.execute(strat)
    bankroll_histories.append(results["bankroll"])
    bets_histories.append(results["bets"])

  total_rounds = [len(session) for session in bankroll_histories]
  average_rounds = sum(total_rounds) / len(total_rounds)
  median_rounds = median(total_rounds)
  winning_rounds = [len(session) for session in bankroll_histories if session[-1] >= session_aim]
  average_winning_rounds = sum(winning_rounds) / len(winning_rounds) if len(winning_rounds) > 0 else 0
  losing_rounds = [len(session) for session in bankroll_histories if session[-1] < session_aim]
  average_losing_rounds = sum(losing_rounds) / len(losing_rounds) if len(losing_rounds) > 0 else 0

  reached_session_aim = [session for session in bankroll_histories if session[-1] >= session_aim]
  success_rate = len(reached_session_aim)/sessions * 100
  reached_half_session_aim = [session for session in bankroll_histories if any(bankroll >= session_aim/2 for bankroll in session)]
  half_success_rate = len(reached_half_session_aim)/sessions * 100

  average_bankroll_after_10_rounds = sum([session[10] if len(session) > 10 else 0 for session in bankroll_histories]) / len(bankroll_histories)
  average_final_bankroll = sum([session[-1] for session in bankroll_histories]) / len(bankroll_histories)

  stats_table = PrettyTable(["Session aim", "1/2 session aim", "Avg rounds", "Median rounds", "Avg W rounds", "Avg L rounds", "Avg @ 10 rounds", "House edge"])
  stats_table.add_row([f"{success_rate:.2f}%", 
                       f"{half_success_rate * 100:.2f}%", 
                       f"{average_rounds:.2f}", 
                       median_rounds, 
                       f"{average_winning_rounds:.2f}",
                       f"{average_losing_rounds:.2f}",
                       f"£{average_bankroll_after_10_rounds:.2f}", 
                       f"{(bankroll - average_final_bankroll)/bankroll * 100:.2f}%"])

  return {"bankroll": bankroll_histories, "bets": bets_histories, "success_rate": success_rate, "stats_table": stats_table}

def print_stats_table(data):
  print(f"\nstrat: {strat}, bankroll: £{bankroll}, bet: £{bet}, session aim: £{session_aim}")
  print(data["stats_table"])

def find_optimal_bet_size(strat):
  bets_range = np.arange(1, bankroll/2, 0.5)
  best_bet = 0
  best_chance = 0
  for bet in bets_range:
    chance = simulate(strat=strat, bet=bet)["success_rate"]
    if chance > best_chance: 
      best_bet = bet 
      best_chance = chance
      # print(f"({strat}) New best bet: {best_bet}, with chance {chance}%")
  return (best_bet, best_chance)

def optimise(optimise_bet=False, win_chance=0, max_rounds=0):
  if win_chance > 50: 
    return print("good one")

  strategies = []
  bets = []
  chances = []

  for strategy in Strategy().strategies.keys():
    chance = simulate(strat=strategy, max_rounds=max_rounds)["success_rate"]
    if optimise_bet: 
      bet, chance = find_optimal_bet_size(strategy)
    if win_chance and chance <= win_chance:
      continue
    strategies.append(strategy)
    chances.append(chance)
    bets.append(bet if optimise_bet else bets)

  if win_chance and not chances: 
    global session_aim
    session_aim -= 0.1 * session_aim
    print(f"changing session aim to: {session_aim}")
    optimise(optimise_bet, win_chance, max_rounds)
    
  if optimise_bet: 
    result = sorted(zip(strategies, bets, chances), key=lambda x: x[2], reverse=True)
  else:
    result = sorted(zip(strategies, chances), key=lambda x: x[1], reverse=True)
    
  return result[:3]


if __name__ == "__main__":
  data = simulate(max_rounds=40)
  print_stats_table(data)
  # plot_bankroll_and_bet(data)
  print(optimise(optimise_bet=True))

