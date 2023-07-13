import random

def get_third(n): 
    if n > 1 and n <= 12: return 1
    if n > 12 and n <= 24: return 2
    if n > 24 and n <= 36: return 3


class Strategy: 
    pockets = ["Red"] * 18 + ["Black"] * 18 + ["Green"] * 1  # European Roulette
    last_pocket = 0

    bankroll = 0 
    bet = 0
    inital_bet = 0
    session_aim = 0
    last_pocket = 1

    def __init__(self, bankroll=100, bet=2.5, session_aim=250, american=False):
        self.bankroll = bankroll
        self.bet = bet
        self.inital_bet = bet
        self.session_aim = session_aim
        if american: self.pockets += ["Green"]

    def execute(self, strategy="always_red"):
        bankroll_history = []
        while self.bankroll > 0 and self.bankroll < self.session_aim:
            self.strategies[strategy](self) # run strategy
            bankroll_history.append(self.bankroll)
        return bankroll_history


    def always_red(self):  
        roll = random.choice(self.pockets)
        if roll == "Red":
            self.bankroll += self.bet
        else:
            self.bankroll -= self.bet

    def martingale(self):
        roll = random.choice(self.pockets)
        if roll == "Red":
            self.bankroll += self.bet
            self.bet = self.inital_bet
        else:
            self.bankroll -= self.bet
            self.bet *= 2

    def irfans(self):
        roll = random.randint(0, 36)
        if roll == 0 or get_third(roll) == get_third(self.last_pocket): 
            self.bankroll -= 2 * self.bet
            # self.bet *= 4
        else:
            self.bankroll += self.bet
            # self.bet = self.inital_bet

        self.last_pocket = roll
        
    def irfans_with_martingale(self):
        roll = random.randint(0, 36)
        if roll == 0 or get_third(roll) == get_third(self.last_pocket): 
            self.bankroll -= 2 * self.bet
            # self.bet *= 4
        else:
            self.bankroll += self.bet
            # self.bet = self.inital_bet

        self.last_pocket = roll

    strategies = {'always_red': always_red, 'martingale': martingale, 'irfans': irfans}



