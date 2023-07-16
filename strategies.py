import random


class Strategy: 
    # European roulette wheel
    roulette = [
        (0, 'Green'),
        (1, 'Red'),
        (2, 'Black'),
        (3, 'Red'),
        (4, 'Black'),
        (5, 'Red'),
        (6, 'Black'),
        (7, 'Red'),
        (8, 'Black'),
        (9, 'Red'),
        (10, 'Black'),
        (11, 'Black'),
        (12, 'Red'),
        (13, 'Black'),
        (14, 'Red'),
        (15, 'Black'),
        (16, 'Red'),
        (17, 'Black'),
        (18, 'Red'),
        (19, 'Red'),
        (20, 'Black'),
        (21, 'Red'),
        (22, 'Black'),
        (23, 'Red'),
        (24, 'Black'),
        (25, 'Red'),
        (26, 'Black'),
        (27, 'Red'),
        (28, 'Black'),
        (29, 'Black'),
        (30, 'Red'),
        (31, 'Black'),
        (32, 'Red'),
        (33, 'Black'),
        (34, 'Red'),
        (35, 'Black'),
        (36, 'Red'),
    ]

    # General parameters
    bankroll = 0 
    bet = 0
    initial_bet = 0
    session_aim = 0

    # Strategy specific
    last_pocket = 1 # irfans 
    streak = 0 # martingale + paroli

    def __init__(self, bankroll=100, bet=2.5, session_aim=250, min_rounds=0, max_rounds=0, american=False):
        self.bankroll = bankroll
        self.bet = bet
        self.initial_bet = bet
        self.session_aim = session_aim if session_aim else float('inf')
        self.min_rounds = min_rounds
        self.max_rounds = max_rounds
        if american: self.roulette += [(-1, 'Green')]

    def execute(self, strategy='always_red'):
        history = {'bankroll': [], 'bets': [], 'rolls': []}
        round = 1

        while 0 < self.bankroll < self.session_aim or round <= self.min_rounds:
            if self.max_rounds and round > self.max_rounds:
                break
            elif strategy.startswith('irfans') and 2 * self.bet > self.bankroll:
                break
            elif self.bet > self.bankroll:
                break

            # run strategy
            roll = random.choice(self.roulette)
            self.strategies[strategy](self, {'pocket': roll[0], 'color': roll[1], })
            # update historical data
            history['bankroll'].append(self.bankroll)
            history['bets'].append(self.bet)
            history['rolls'].append(roll)
            round += 1

        return history

    def update_bankroll(self, win, dozens=False):
        if win:
            self.bankroll += self.bet 
        else:
            self.bankroll -= self.bet if not dozens else 2 * self.bet

    def reset_bet(self):
        self.bet = self.initial_bet

    # ===================================
    # ------ EVEN ODDS STRATEGIES -------
    # ===================================
    # bet on Red every time
    def always_red(self, roll):  
        win = roll['color'] == 'Red'
        self.update_bankroll(win)

    # double bets on loss and reset on win
    def martingale(self, roll):
        win = roll['color'] == 'Red'
        self.update_bankroll(win)
        if win:
            self.reset_bet()
        else:
            self.bet *= 2

    # increase and decrease bets by 1 unit on win and loss respectively
    def dalembert(self, roll):
        win = roll['color'] == 'Red'
        self.update_bankroll(win)
        if win:
            self.bet += self.initial_bet 
        elif self.bet > self.initial_bet:
            self.bet -= self.initial_bet

    # increase bets by 1 unit and reset after 3 wins
    def paroli(self, roll):
        win = roll['color'] == 'Red'
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


    # ================================
    # ------ DOZENS STRATEGIES -------
    # ================================
    # Bet on 2/3 dozens, based on last dozen rolled 
    def irfans(self, roll):
        same_dozens = get_dozen(roll['pocket']) == get_dozen(self.last_pocket)
        win = not same_dozens and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        self.last_pocket = roll['pocket']

    # Martingale + 2/3 dozens
    def irfans_with_martingale(self, roll):
        same_dozens = get_dozen(roll['pocket']) == get_dozen(self.last_pocket)
        win = not same_dozens and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        if win: 
            self.reset_bet()
        else:
            self.bet *= 2
        self.last_pocket = roll['pocket']
    
    # Dalembert + 2/3 dozens
    def irfans_with_dalembert(self, roll):
        same_dozens = get_dozen(roll['pocket']) == get_dozen(self.last_pocket)
        win = not same_dozens and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        if win:
            self.bet += self.initial_bet 
        elif self.bet > self.initial_bet:
            self.bet -= self.initial_bet
        self.last_pocket = roll['pocket']

    # Paroli + 2/3 dozens
    def irfans_with_paroli(self, roll):
        last_dozen = get_dozen(roll['pocket']) == get_dozen(self.last_pocket)
        win = not last_dozen and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        if win:
            self.bet *= 2
            self.streak += 1
            if self.streak == 3:
                self.reset_bet()
        else:
            self.bet = self.initial_bet
            self.streak = 0
        self.last_pocket = roll['pocket']

    # ==============================
    # ------ MISC STRATEGIES -------
    # ==============================


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


def get_dozen(n): 
    if n > 0 and n <= 12: return 1
    if n > 12 and n <= 24: return 2
    if n > 24 and n <= 36: return 3

def pocket_not_0(roll): 
    return roll['pocket'] != 0 and roll['pocket'] != -1