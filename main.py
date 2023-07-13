import random
import seaborn as sns
import matplotlib.pyplot as plt

def martingale(bankroll):
    bet = 2.5
    pockets = ["Red"] * 18 + ["Black"] * 18 + ["Green"] * 1
    bankroll_history = []
    while bankroll > 0:
        if bet > bankroll:
            bet = bankroll
        roll = random.choice(pockets)
        if roll == "Red":
            bankroll += bet
            bet = 2.5
        else:
            bankroll -= bet
            bet *=2
        bankroll_history.append(bankroll)
    return bankroll_history
    
martingale(bankroll=100)


for i in range(6):
    plt.plot(martingale(bankroll=150), linewidth=2)
    
plt.xlabel("Number of Games", fontsize=18, fontweight="bold")
plt.ylabel("Bankroll", fontsize=18, fontweight="bold")
plt.xticks(fontsize=16, fontweight="bold")
plt.yticks(fontsize=16, fontweight="bold")
plt.title("Bankroll Over Time", fontsize=22, fontweight="bold")
plt.show()