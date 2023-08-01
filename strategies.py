import random
import math

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

class Strategy: 
    def __init__(self, bankroll=100, bet=2.5, session_aim=250, min_rounds=0, max_rounds=0, american=False):
        self.bankroll = bankroll
        self.bet_unit = bet
        self.curr_bet = bet
        self.session_aim = session_aim if session_aim else float('inf')
        self.min_rounds = min_rounds
        self.max_rounds = max_rounds
        
        # meta
        self.history = {'bankroll': [], 'bets': [], 'rolls': []}
        self.round = 1
        global roulette
        if american: roulette += [(-1, 'Green')]

        # strategy specific
        self.streak = 0 # martingale + paroli + hollandish
        self.progression = [] # johnson progression
        self.progression_pointer = 0 # johnson progression

    def execute(self, strategy='always_red'):
        while 0 < self.bankroll < self.session_aim or self.round <= self.min_rounds:
            if self.max_rounds and self.round > self.max_rounds:
                break
            elif strategy.startswith('irfans') and 2 * self.curr_bet > self.bankroll:
                break
            elif self.curr_bet > self.bankroll:
                break

            # run strategy
            roll = random.choice(roulette)
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
        self.bet_unit = math.ceil(1/9 * self.bankroll)
        if self.round == 1: 
            self.curr_bet = self.bet_unit * 3

        win = roll['color'] == "Red"
        if win: 
            self.bankroll += self.curr_bet
            self.curr_bet = self.bet_unit * 3
        else:
            self.bankroll -= self.curr_bet
            self.curr_bet = self.bet_unit * 6


    # standard labouchere progression with lenght based on profit goal 
    def labouchere(self, roll):
        win = roll['color'] == 'Red'
        if self.round == 1: 
            unit, progression_len = find_progression_len(self)
            self.progression = [unit * i for i in range(progression_len)]

        bet_units = get_round_units(self)
        self.curr_bet = bet_units * self.bet_unit
        self.update_bankroll(win)

        if win: 
            self.progression = self.progression[1:-1] # remove first and last elements
        else:
            self.progression.append(bet_units)
            

    # https://www.roulettelife.com/index.php?topic=9.0
    def johnson_progression(self, roll): 
        win = roll['color'] == 'Red'
        if self.round == 1: 
            progression_len = 20 if not self.min_rounds else self.min_rounds
            unit = math.ceil((self.session_aim - self.bankroll) / self.bet_unit)
            self.progression = [unit * i for i in range(progression_len)]

        bet_units = get_round_units(self)
        self.curr_bet = bet_units * self.bet_unit
        self.update_bankroll(win)

        if win: 
            self.progression = self.progression[1:-1] # remove first and last elements
        else: 
            distribute_losses(self, bet_units)

    # https://www.888casino.com/blog/hollandish-roulette-system
    def hollandish(self, roll):
        win = roll['color'] == 'Red'
        self.update_bankroll(win)

        if win: 
            self.streak -= 1 
            if self.streak == 0: 
                self.curr_bet += 2 * self.bet_unit
        else:
            self.streak += 1

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
        self.curr_bet = 8 * self.bet_unit
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

    # https://www.888casino.com/blog/4-pillars-system-notes-madman
    def four_pillars(self, roll):
        self.curr_bet = 6 * self.bet_unit
        pocket = roll['pocket']

        if pocket in range(4, 10) or pocket in range(25, 31):
            self.bankroll -= self.bet_unit # what ?
        else: 
            self.bankroll -= self.bet_unit * 2
            
        if pocket in [19, 20, 22, 23, 31, 32, 34, 35]:
            self.bankroll += self.bet_unit * 3
        else: 
            self.bankroll -= self.bet_unit * 2
            
        if pocket in [14, 15, 17, 18]:
            self.bankroll += self.bet_unit * 12
        else: 
            self.bankroll -= self.bet_unit * 2
            

    # https://www.888casino.com/blog/positional-roulette#how-to-play-positional-roulette
    def positional_roulette(self, roll):
        self.curr_bet = self.bet_unit * 8
        if self.round < 38:
            pass # build data on uncommon numbers
        else:
            winning_pockets = find_positional_numbers(self) # bet on 8 numbers
            if roll["pocket"] in winning_pockets:
                self.bankroll += self.bet_unit * (35 - len(winning_pockets)-1)
            else: 
                self.bankroll -= self.bet_unit * len(winning_pockets)

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
        'labouchere': labouchere,
        'johnson_progression': johnson_progression,
        'four_pillars': four_pillars,
        'hollandish': hollandish,
        'positional_roulette': positional_roulette
    }


def get_dozen(n): 
    if n > 0 and n <= 12: return 1
    if n > 12 and n <= 24: return 2
    if n > 24 and n <= 36: return 3

def pocket_not_0(roll): 
    return roll['pocket'] != 0 and roll['pocket'] != -1

def last_roll(self):
    return self.history['rolls'][-1][0] if self.history['rolls'] else 1

def find_progression_len(self):
    units_to_make = math.ceil((self.session_aim - self.bankroll) / self.bet_unit)
    i = 3 # min progression len
    while True: 
        total = 0
        unit = math.ceil(units_to_make / i)
        for x in range(i):
            total += unit * x
        if self.bankroll >= total: 
            break
        i += 1
    return (unit, i)

def get_round_units(self):
    bet_units = 0
    if not self.progression: 
        Exception("Progression is empty")
    elif len(self.progression) == 1: 
        bet_units = self.progression[0]
    else:
        bet_units = self.progression[0] + self.progression[-1]
    return bet_units

def distribute_losses(self, to_distribute):
    while to_distribute > 0: 
        if self.progression_pointer > len(self.progression) - 1:
            self.progression_pointer = 0
        self.progression[self.progression_pointer] += 1
        self.progression_pointer += 1
        to_distribute -= 1

def find_positional_numbers(self):
    all_n = set(range(1, 37))
    appeared_n = set(roll[0] for roll in self.history['rolls'])
    uncommon_n = all_n - appeared_n

    prev_pocket, prev_color = self.history["rolls"][-1]
    if prev_color == "Green": prev_color = "Red"
    selected_pockets = []

    def get_next_pocket_index(index):
        return (index + 1) % len(roulette)

    def get_prev_pocket_index(index):
        return (index - 1) % len(roulette)
    
    cycle_count = 0
    i = get_next_pocket_index(prev_pocket)
    while len(selected_pockets) < 8:
        n, color = roulette[i]
        if color == prev_color and n not in selected_pockets and n not in uncommon_n:
            selected_pockets.append(n)
        else:
            cycle_count += 1

        if cycle_count >= len(roulette):
            break  # If we've gone through all pockets without finding new ones, break out of the loop

        if len(selected_pockets) < 4: 
            i = get_next_pocket_index(i) # find next 4 numbers
        else:
            i = get_prev_pocket_index(i) # find previous 4 numbers
    return selected_pockets