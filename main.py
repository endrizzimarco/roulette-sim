from simulate import simulate, optimise
from prettytable import PrettyTable
import matplotlib.pyplot as plt
from statistics import median
import seaborn as sns


# TODO: possibility to choose between baccarat player and banker
params = {
  "sessions": 2**14, # 16384
  "strat": "hollandish",
  "data": {
    "baccarat": False,
    "bankroll": 50,
    "bet_unit": 5,
    "profit_goal": 100,
    "min_rounds": 0,
    "max_rounds": 0,
    "table_limits": 0,
  }
}

def plot_bankroll_and_bet(data):
  sns.set_style("darkgrid")
  plt.ylabel("Amount (£)")
  plt.xlabel("Rounds")
  plt.title(f"Bankroll and Bet over time for final session ({params['strat']})")
  plt.plot(data["bankroll_histories"][-1], label ="Bankroll")
  plt.plot(data["bets_histories"][-1], label="Bet")
  plt.legend()
  plt.show()

def print_stats_table(params, history):
  bankroll_histories = history["bankrolls"]
  profit_goal = params["data"]["profit_goal"]
  bankroll = params["data"]["bankroll"]

  reached_profit_goal = [session for session in bankroll_histories if session[-1] >= profit_goal]
  success_rate = len(reached_profit_goal)/params["sessions"] * 100
  reached_close_profit_goal = [session for session in bankroll_histories if any(bankroll >= profit_goal*0.75 for bankroll in session)]
  close_success_rate = len(reached_close_profit_goal)/params["sessions"] * 100
  wl_for_session = [(wl.count("win")/len(wl)) * 100 for wl in history["wl"]]
  average_wl_for_session = sum(wl_for_session) / len(wl_for_session)

  total_rounds = [len(session) for session in bankroll_histories]
  median_rounds = median(total_rounds)
  winning_rounds = [len(session) for session in bankroll_histories if session[-1] >= profit_goal]
  average_winning_rounds = sum(winning_rounds) / len(winning_rounds) if len(winning_rounds) > 0 else 0
  losing_rounds = [len(session) for session in bankroll_histories if session[-1] <= 0]
  average_losing_rounds = sum(losing_rounds) / len(losing_rounds) if len(losing_rounds) > 0 else 0

  average_bankroll_after_10_rounds = sum([session[10] if len(session) > 10 else 0 for session in bankroll_histories]) / len(bankroll_histories)
  average_final_bankroll = sum([session[-1] for session in bankroll_histories]) / len(bankroll_histories)

  stats_table = PrettyTable(["Session aim", "3/4 session aim", "Avg W/L for session", "Median rounds", "Avg W rounds", "Avg L rounds", "Avg @ 10 rounds", "House edge"])
  stats_table.add_row([f"{success_rate:.2f}%", 
                       f"{close_success_rate:.2f}%", 
                       f"{average_wl_for_session:.2f}%",
                       int(median_rounds), 
                       f"{average_winning_rounds:.2f}",
                       f"{average_losing_rounds:.2f}",
                       f"£{average_bankroll_after_10_rounds:.2f}", 
                       f"{(bankroll - average_final_bankroll)/bankroll * 100:.2f}%"])

  print(bankroll_histories[-1])
  print(history["wl"][-1])
  print("progression", history["progressions"][-1])
  print("bets", history["bets"][-1])
  print(f"\nstrat: {params['strat']}, bankroll: £{bankroll}, bet: £{params['data']['bet_unit']}, session aim: £{profit_goal}")
  print(stats_table)


if __name__ == "__main__":
  # history = simulate(params)
  # print_stats_table(params, history)
  # plot_bankroll_and_bet(data)
  print(optimise(params, optimise_bet=False)) # optimise(params, optimise_bet=False, win_chance=0)