import random

def get_third(n): 
    if n > 0 and n <= 12: return 1
    if n > 12 and n <= 24: return 2
    if n > 24 and n <= 36: return 3


class Strategy: 
    pockets = ["Red"] * 18 + ["Black"] * 18 + ["Green"] * 1  # European Roulette
    bankroll = 0 
    bet = 0
    inital_bet = 0
    session_aim = 0
    
    last_pocket = 1 # irfans 
    streak = 0 # paroli

    def __init__(self, bankroll=100, bet=2.5, session_aim=250, american=False):
        self.bankroll = bankroll
        self.bet = bet
        self.inital_bet = bet
        self.session_aim = session_aim
        if american: self.pockets += ["Green"]

    def execute(self, strategy="always_red"):
        bankroll_history = []

        while 0 < self.bankroll < self.session_aim: 
            if strategy.startswith("irfans") and 2 * self.bet > self.bankroll:
                break
            elif self.bet > self.bankroll:
                break
            
            # run strategy
            self.strategies[strategy](self) 
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
        else:
            self.bankroll += self.bet
        self.last_pocket = roll

    def irfans_with_martingale(self):
        roll = random.randint(0, 36)
        if self.streak >= 3:
            self.bet = self.inital_bet
        if roll == 0 or get_third(roll) == get_third(self.last_pocket): 
            self.bankroll -= 2 * self.bet
            self.bet *= 2
        else:
            self.bankroll += self.bet
            self.bet = self.inital_bet
            self.streak += 1
            if self.streak == 3:
                self.bet = self.bet * 2
        self.last_pocket = roll
        
    def paroli(self): 
        roll = random.choice(self.pockets)
        if roll == "Red":
            self.bankroll += self.bet
            self.bet *= 2
            self.streak += 1

            if self.streak == 3:
                self.bet = self.inital_bet
        else:
            self.bankroll -= self.bet
            self.bet *= self.inital_bet

    def irfans_with_paroli(self):
        roll = random.randint(0, 36)
        if roll == 0 or get_third(roll) == get_third(self.last_pocket): 
            self.bankroll -= 2 * self.bet
            self.bet *= self.inital_bet
        else:
            self.bankroll += self.bet
            self.bet *= 2
            self.streak += 1

            if self.streak == 3:
                self.bet = self.inital_bet
        self.last_pocket = roll

    def dalembert(self):
        roll = random.choice(self.pockets)
        if roll == "Red":
            self.bankroll += self.bet
            self.bet += self.inital_bet
        else:
            self.bankroll -= self.bet
            self.bet -= self.inital_bet if self.bet > self.inital_bet else 0

    def irfans_with_dalembert(self):
        roll = random.randint(0, 36)
        if roll == 0 or get_third(roll) == get_third(self.last_pocket): 
            self.bankroll -= 2 * self.bet
            self.bet += self.inital_bet
        else:
            self.bankroll += self.bet
            self.bet -= self.inital_bet if self.bet > self.inital_bet else 0
        self.last_pocket = roll


    strategies = {
        'always_red': always_red, 
        'martingale': martingale, 
        'paroli': paroli, 
        'dalembert': dalembert,
        'irfans': irfans, 
        'irfans_with_martingale': irfans_with_martingale, 
        'irfans_with_paroli': irfans_with_paroli,
        'irfans_with_dalembert': irfans_with_dalembert,
    }


