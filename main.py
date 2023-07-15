from strategies import Strategy
from statistics import median
import seaborn as sns
import matplotlib.pyplot as plt
from prettytable import PrettyTable

strat = "martingale"
bankroll = 50 
bet = 5
session_aim = 100

def plot_bankroll_and_bet(bankroll_histories, bets_histories, strat):
  sns.set_style("darkgrid")
  plt.ylabel("Amount (£)")
  plt.xlabel("Rounds")
  plt.title(f"Bankroll and Bet over time for final session ({strat})")
  plt.plot(bankroll_histories[-1], label ="Bankroll")
  plt.plot(bets_histories[-1], label="Bet")
  plt.legend()
  plt.show()

if __name__ == "__main__":
  sessions = 2**16 # 65,536
  reached_session_aim = 0
  bankroll_histories = []
  bets_histories = []
  for i in range(sessions):
    strategy = Strategy(bankroll, bet, session_aim)
    results = strategy.execute(strat)
    bankroll_histories.append(results["bankroll"])
    bets_histories.append(results["bets"])

  total_rounds = [len(session) for session in bankroll_histories]
  average_rounds = sum(total_rounds) / len(total_rounds)
  median_rounds = median(total_rounds)

  reached_session_aim = [session for session in bankroll_histories if session[-1] >= session_aim]
  reached_half_session_aim = [session for session in bankroll_histories if any(bankroll >= session_aim/2 for bankroll in session)]

  average_bankroll_after_10_rounds = sum([session[10] if len(session) > 10 else 0 for session in bankroll_histories]) / len(bankroll_histories)
  max_bet = max([max(session) for session in bets_histories])

  table = PrettyTable(["Reached session aim", "Reached half session aim", "Average rounds", "Median rounds", "Average bankroll after 10 rounds", "Max bet"])
  table.add_row([f"{len(reached_session_aim)/sessions * 100:.2f}%", f"{len(reached_half_session_aim)/sessions * 100:.2f}%", f"{average_rounds:.2f}", median_rounds, f"£{average_bankroll_after_10_rounds:.2f}", f"£{max_bet}"])
  print(table)
  
  plot_bankroll_and_bet(bankroll_histories, bets_histories, strat)




