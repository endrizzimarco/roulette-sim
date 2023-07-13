import random
import seaborn as sns
import matplotlib.pyplot as plt

def always_red():  
    total_cash = 150
    pockets = ["Red"] * 18 + ["Black"] * 18 + ["Green"] * 1
    history = []
    while total_cash > 0:
        roll = random.choice(pockets)
        if roll == "Red":
            total_cash += 10
        else:
            total_cash -= 10
        history.append(total_cash)
    print(len(history))
    return history
    

sns.set(rc={'figure.figsize':(11.7,8.27)})
for i in range(4):
    plt.plot(always_red(), linewidth=2)
    
plt.xlabel("Number of Games", fontsize=18, fontweight="bold")
plt.ylabel("Bankroll", fontsize=18, fontweight="bold")
plt.xticks(fontsize=16, fontweight="bold")
plt.yticks(fontsize=16, fontweight="bold")
plt.title("Bankroll Over Time", fontsize=22, fontweight="bold")
plt.show()