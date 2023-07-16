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

    def __init__(self, bankroll=100, bet=2.5, session_aim=250, min_rounds=0, max_rounds=0, american=False):
        self.bankroll = bankroll
        self.bet_unit = bet
        self.curr_bet = bet
        self.session_aim = session_aim if session_aim else float('inf')
        self.min_rounds = min_rounds
        self.max_rounds = max_rounds
        self.history = {'bankroll': [], 'bets': [], 'rolls': []}
        self.round = 1
        self.streak = 0 # martingale + paroli
        if american: self.roulette += [(-1, 'Green')]

    def execute(self, strategy='always_red'):
        while 0 < self.bankroll < self.session_aim or self.round <= self.min_rounds:
            if self.max_rounds and self.round > self.max_rounds:
                break
            elif strategy.startswith('irfans') and 2 * self.curr_bet > self.bankroll:
                break
            elif self.curr_bet > self.bankroll:
                break

            # run strategy
            roll = random.choice(self.roulette)
            self.strategies[strategy](self, {'pocket': roll[0], 'color': roll[1]})
            # update historical data
            self.history['bankroll'].append(self.bankroll)
            self.history['bets'].append(self.curr_bet)
            self.history['rolls'].append(roll)
            self.round += 1

        return self.history

    def update_bankroll(self, win, dozens=False):
        if win:
            self.bankroll += self.curr_bet 
        else:
            self.bankroll -= self.curr_bet if not dozens else 2 * self.curr_bet

    def reset_bet(self):
        self.curr_bet = self.bet_unit

    # ======================================
    # ------ EVEN CHANCES STRATEGIES -------
    # ======================================
    # bet on red every time
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
            self.curr_bet *= 2

    # increase and decrease bets by 1 unit on win and loss respectively
    def dalembert(self, roll):
        win = roll['color'] == 'Red'
        self.update_bankroll(win)
        if win:
            self.curr_bet += self.bet_unit 
        elif self.curr_bet > self.bet_unit:
            self.curr_bet -= self.bet_unit

    # increase bets by 1 unit and reset after 3 wins
    def paroli(self, roll):
        win = roll['color'] == 'Red'
        self.update_bankroll(win)
        if win:
            self.curr_bet *= 2
            self.streak += 1
            if self.streak == 3:
                self.reset_bet()
        else:
            self.curr_bet = self.bet_unit
            self.streak = 0

    # A simpler version of this: https://www.888casino.com/blog/tier-et-tout
    # TODO: come back to this
    def tier_et_tout(self, roll):
        self.bet_unit = int(1/9 * self.bankroll)
        if self.round == 1: 
            self.curr_bet = self.bet_unit * 3

        win = roll['color'] == "Red"
        if win: 
            self.bankroll += self.curr_bet
            self.curr_bet = self.bet_unit * 3
        else:
            self.bankroll -= self.curr_bet
            self.curr_bet = self.bet_unit * 6


    # TODO: 
    # def labouchere(self):
        
    # TODO: 
    # def oscars_grind(self):


    # ================================
    # ------ DOZENS STRATEGIES -------
    # ================================
    # Bet on 2/3 dozens, based on last dozen rolled 
    def irfans(self, roll):
        same_last_dozen = get_dozen(roll['pocket']) == get_dozen(last_roll(self))
        win = not same_last_dozen and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        self.last_roll = roll['pocket']

    # Martingale + 2/3 dozens
    def irfans_with_martingale(self, roll):
        same_last_dozen = get_dozen(roll['pocket']) == get_dozen(last_roll(self))
        win = not same_last_dozen and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        if win: 
            self.reset_bet()
        else:
            self.curr_bet *= 2
        self.last_roll = roll['pocket']
    
    # Dalembert + 2/3 dozens
    def irfans_with_dalembert(self, roll):
        same_last_dozen = get_dozen(roll['pocket']) == get_dozen(last_roll(self))
        win = not same_last_dozen and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        if win:
            self.curr_bet += self.bet_unit 
        elif self.curr_bet > self.bet_unit:
            self.curr_bet -= self.bet_unit
        self.last_roll = roll['pocket']

    # Paroli + 2/3 dozens
    def irfans_with_paroli(self, roll):
        same_last_dozen = get_dozen(roll['pocket']) == get_dozen(last_roll(self))
        win = not same_last_dozen and pocket_not_0(roll)
        self.update_bankroll(win, dozens=True)
        if win:
            self.curr_bet *= 2
            self.streak += 1
            if self.streak == 3:
                self.reset_bet()
        else:
            self.curr_bet = self.bet_unit
            self.streak = 0
        self.last_roll = roll['pocket']

    # ==============================
    # ------ MISC STRATEGIES -------
    # ==============================
    # https://www.888casino.com/blog/kavouras-bet
    def kavouras(self, roll):
        pocket = roll['pocket']
        # corner
        if pocket in range(0, 4): 
            self.bankroll += self.bet_unit 
        else: 
            self.bankroll -= self.bet_unit

        # double street
        if pocket in range(31, 37):
            self.bankroll += self.bet_unit * 4 
        else: 
            self.bankroll -= self.bet_unit * 2

        # splits
        splits = list(range(8, 12)) + list(range(15, 19)) + list(range(17, 21)) + list(range(27, 31))
        if pocket in splits:
            self.bankroll += self.bet_unit * 10
        else:
            self.bankroll -= self.bet_unit * 5


    strategies = {
        'always_red': always_red, 
        'martingale': martingale, 
        'paroli': paroli, 
        'dalembert': dalembert,
        'irfans': irfans, 
        'irfans_with_martingale': irfans_with_martingale, 
        'irfans_with_paroli': irfans_with_paroli,
        'irfans_with_dalembert': irfans_with_dalembert,
        'kavouras': kavouras,
        'tier_et_tout': tier_et_tout,
    }


def get_dozen(n): 
    if n > 0 and n <= 12: return 1
    if n > 12 and n <= 24: return 2
    if n > 24 and n <= 36: return 3

def pocket_not_0(roll): 
    return roll['pocket'] != 0 and roll['pocket'] != -1

def last_roll(self):
    return self.history['rolls'][-1][0] if self.history['rolls'] else 1