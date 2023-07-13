from strategies import Strategy
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":
  plays = 2**12 # 1024
  reached_session_aim = 0
  for i in range(plays):
    strategy = Strategy(bankroll=50, bet=2.5, session_aim=1000)
    results = strategy.execute("irfans")
    if max(results) >= strategy.session_aim: 
      reached_session_aim += 1
  print(f"Win probability for a session: {reached_session_aim/plays * 100}%")
    # print(f"Total plays: {len(results)}")
    # print(f"Max bankroll: {max(results)}")

# for i in range(6):
#     plt.plot(Strategy(bankroll=50, bet=2.5, session_aim=1000).execute("irfans"), linewidth=2)
    
# plt.xlabel("Number of Games", fontsize=18, fontweight="bold")
# plt.ylabel("Bankroll", fontsize=18, fontweight="bold")
# plt.xticks(fontsize=16, fontweight="bold")
# plt.yticks(fontsize=16, fontweight="bold")
# plt.title("Bankroll Over Time", fontsize=22, fontweight="bold")
# plt.show()

