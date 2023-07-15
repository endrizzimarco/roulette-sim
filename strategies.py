import random


class Strategy: 
    pockets = ["Red"] * 18 + ["Black"] * 18 + ["Green"] * 1  # European Roulette
    bankroll = 0 
    bet = 0
    initial_bet = 0
    session_aim = 0
    
    last_pocket = 1 # irfans 
    streak = 0 # martingale + paroli + oscars

    def __init__(self, bankroll=100, bet=2.5, session_aim=250, american=False):
        self.bankroll = bankroll
        self.bet = bet
        self.initial_bet = bet
        self.session_aim = session_aim
        if american: self.pockets += ["Green"]

    def execute(self, strategy="always_red"):
        history = {"bankroll": [], "bets": []}

        while 0 < self.bankroll < self.session_aim: 
            if strategy.startswith("irfans") and 2 * self.bet > self.bankroll:
                break
            elif self.bet > self.bankroll:
                break

            # run strategy
            self.strategies[strategy](self) 
            history["bankroll"].append(self.bankroll)
            history["bets"].append(self.bet)

        return history

    def update_bankroll(self, win, irfans=False):
        if win:
            self.bankroll += self.bet 
        else:
            self.bankroll -= self.bet if not irfans else 2 * self.bet

    def reset_bet(self):
        self.bet = self.initial_bet

    # =========================
    # ------ STRATEGIES -------
    # =========================
    # bet on red every time
    def always_red(self):  
        win = random.choice(self.pockets) == "Red"
        self.update_bankroll(win)

    # double bets on loss and reset on win
    def martingale(self):
        win = random.choice(self.pockets) == "Red"
        self.update_bankroll(win)
        if win:
            self.reset_bet()
        else:
            self.bet *= 2

    # increase and decrease bets by 1 unit on win and loss respectively
    def dalembert(self):
        win = random.choice(self.pockets) == "Red"
        self.update_bankroll(win)
        if win:
            self.bet += self.initial_bet 
        elif self.bet > self.initial_bet:
            self.bet -= self.initial_bet

    # increase bets by 1 unit and reset after 3 wins
    def paroli(self):
        win = random.choice(self.pockets) == "Red"
        self.update_bankroll(win)
        if win:
            self.bet *= 2
            self.streak += 1
            if self.streak == 3:
                self.reset_bet()
        else:
            self.bet = self.initial_bet
            self.streak = 0
            
    # def tier_et_tout(self):

    # TODO: 
    # def labouchere(self):
        
    # TODO: 
    # def oscars_grind(self):



    # Bet on 2/3 dozens
    def irfans(self):
        roll = random.randint(0, 36)
        win = roll != 0 and get_third(roll) != get_third(self.last_pocket)
        self.update_bankroll(win, irfans=True)
        self.last_pocket = roll

    # Bet on 2/3 dozens + 0.05 of the bet on 0
    def irfans_with_0(self):
        roll = random.randint(0, 36)
        bet_on_zero = self.bet * 0.05
        if roll == 0:
            self.bankroll += (bet_on_zero * 35) - (2 * self.bet)
        elif get_third(roll) == get_third(self.last_pocket): 
            self.bankroll -= (2 * self.bet) + bet_on_zero
        else:
            self.bankroll += self.bet - bet_on_zero
        self.last_pocket = roll

    # Martingale + 2/3 dozens
    def irfans_with_martingale(self):
        roll = random.randint(0, 36)
        win = roll != 0 and get_third(roll) != get_third(self.last_pocket)
        self.update_bankroll(win, irfans=True)
        if win: 
            self.reset_bet()
        else:
            self.bet *= 2
        self.last_pocket = roll
    
    # Dalembert + 2/3 dozens
    def irfans_with_dalembert(self):
        roll = random.randint(0, 36)
        win = roll != 0 and get_third(roll) != get_third(self.last_pocket)
        self.update_bankroll(win, irfans=True)
        if win:
            self.bet += self.initial_bet 
        elif self.bet > self.initial_bet:
            self.bet -= self.initial_bet
        self.last_pocket = roll

    # Paroli + 2/3 dozens
    def irfans_with_paroli(self):
        roll = random.randint(0, 36)
        win = roll != 0 and get_third(roll) != get_third(self.last_pocket)
        self.update_bankroll(win, irfans=True)
        if win:
            self.bet *= 2
            self.streak += 1
            if self.streak == 3:
                self.reset_bet()
        else:
            self.bet = self.initial_bet
            self.streak = 0
        self.last_pocket = roll


    strategies = {
        'always_red': always_red, 
        'martingale': martingale, 
        'paroli': paroli, 
        'dalembert': dalembert,
        'irfans': irfans, 
        'irfans_with_0': irfans_with_0,
        'irfans_with_martingale': irfans_with_martingale, 
        'irfans_with_paroli': irfans_with_paroli,
        'irfans_with_dalembert': irfans_with_dalembert,
    }


def get_third(n): 
    if n > 0 and n <= 12: return 1
    if n > 12 and n <= 24: return 2
    if n > 24 and n <= 36: return 3

