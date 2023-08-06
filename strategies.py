from abc import ABC, abstractmethod
import random
import math


# Constants
ROULETTE = [(0, 'Green'), (1, 'Red'), (2, 'Black'), (3, 'Red'), (4, 'Black'), (5, 'Red'),(6, 'Black'), (7, 'Red'), (8, 'Black'), (9, 'Red'), (10, 'Black'), (11, 'Black'), (12, 'Red'), (13, 'Black'), (14, 'Red'), (15, 'Black'), (16, 'Red'), (17, 'Black'), (18, 'Red'), (19, 'Red'), (20, 'Black'), (21, 'Red'), (22, 'Black'), (23, 'Red'), (24, 'Black'), (25, 'Red'), (26, 'Black'), (27, 'Red'), (28, 'Black'), (29, 'Black'), (30, 'Red'), (31, 'Black'), (32, 'Red'), (33, 'Black'), (34, 'Red'), (35, 'Black'), (36, 'Red'),]
BACCARAT_ODDS = [50.68, 49.32] # [banker (no, viz), player]


# Set the odds based on the game played (for even odds strategies only)
class Game:
    def __init__(self, roulette=ROULETTE, baccarat_odds=BACCARAT_ODDS, baccarat=False, american=False):
        self.roulette = roulette
        self.baccarat = baccarat
        self.baccarat_odds = baccarat_odds
        if american: 
            self.roulette += [(-1, 'Green')]

    def roll(self):
        if self.baccarat:
            return (None, random.choices(['Red', 'Black'], weights=self.baccarat_odds)[0])
        else: 
            return random.choice(self.roulette)


class CasinoSession: 
    def __init__(self, bankroll=100, bet_unit=2.5, profit_goal=250, min_rounds=0, max_rounds=0, american=False, baccarat=False):
        self.bankroll = bankroll
        self.bet_unit = bet_unit
        self.curr_bet = bet_unit
        self.min_rounds = min_rounds
        self.max_rounds = max_rounds
        self.profit_goal = profit_goal if profit_goal else float('inf')
        # meta
        self.game = Game(baccarat=baccarat, american=american)
        self.strategy = None
        self.history = {'bankroll': [bankroll], 'bets': [], 'rolls': [], 'progression': [], 'wl': []}
        self.round = 1

        # strategy specific
        self.progression = [] # johnson progression
        self.pointer = 0 # johnson progression + manhattan 
        self.level = 0 # guetting progression
        
        self.strategies = {
            'always_red': AlwaysRed, 
            'irfans': Irfans,
            'martingale': Martingale,
            'grand_martingale': GrandMartingale,
            'dalembert': Dalembert,
            'paroli': Paroli,
            'fibonacci': Fibonacci,
            'hollandish': Hollandish,
            'tier_et_tout': TierEtTout,
            '1326': OneThreeTwoSix,
            '148': OneFourEight,
            'manhattan': Manhattan,
            'standard_guetting': StandardGuetting,
            'optimal_guetting': OptimalGuetting,
            'labouchere': Labouchere,
            'johnson_progression': JohnsonProgression,
            'kavouras': Kavouras,
            'four_pillars': FourPillars,
            'sixsixsix': SixSixSix,
            'positional_roulette': PositionalRoulette,
        }

    def execute(self, strategy='always_red'):
        if not self.strategy: 
            self.strategy = self.strategies[strategy](self)

        while self.should_continue(self.strategy):
            roll = self.game.roll()
            self.strategy.execute({"pocket": roll[0], "color": roll[1]})
            self.update_history(roll)
            self.round += 1
        return self.history

    def should_continue(self, strategy):
        # Check if the bankroll is greater than zero and less than the profit goal.
        bankroll_within_limits = 0 < self.bankroll < self.profit_goal
        # Check if the minimum number of rounds is specified and if the current round exceeds it.
        min_rounds_not_reached = self.min_rounds and self.round <= self.min_rounds
        # Check if the maximum number of rounds is specified and if the current round exceeds it.
        max_rounds_reached = self.max_rounds and self.round > self.max_rounds
        # Check whether the current bet is more than the available bankroll (money does not grow on trees).
        bet_exceeds_bankroll = 2 * self.curr_bet > self.bankroll if strategy.use_dozens else self.curr_bet > self.bankroll

        # As long as the bankroll is within limits or the minimum number of rounds is not reached, continue betting 
        # (unless the maximum number of rounds is reached or the bet exceeds the bankroll)
        continue_betting = (bankroll_within_limits or min_rounds_not_reached) and not (max_rounds_reached or bet_exceeds_bankroll)

        return continue_betting

    def update_history(self, roll):
        self.history['bankroll'].append(self.bankroll)
        self.history['bets'].append(self.curr_bet)
        self.history['rolls'].append(roll)

    def update_bankroll(self, win, dozens=False):
        if win:
            self.bankroll += self.curr_bet if not self.game.baccarat else 0.95 * self.curr_bet
            self.history['wl'].append('win')
        else:
            self.bankroll -= self.curr_bet if not dozens else 2 * self.curr_bet
            self.history['wl'].append('lose')
            
    def insufficent_funds(self, units):
        self.curr_bet = units
        return self.curr_bet > self.bankroll

    def reset_bet(self):
        self.curr_bet = self.bet_unit

    def check_and_handle_insufficient_funds(self):
        if self.bankroll <= 0: 
            return
        elif self.curr_bet > self.bankroll:
            self.curr_bet = self.bankroll


class BettingStrategy(ABC):
    def __init__(self, session_instance):
        self.session = session_instance
        self.use_dozens = False

    def even_odds_strat(self, roll):
        win = roll['color'] == 'Red'
        self.session.update_bankroll(win)
        return win

    # Apply the strategy on dozens with the "Irfans" strategy
    def dozens_strat(self, roll):
        curr_dozen = Irfans.get_dozen(roll['pocket'])
        prev_dozen = Irfans.get_dozen(Irfans.last_roll(self.session))
        same_last_dozen = prev_dozen == curr_dozen
        win = not same_last_dozen and Irfans.pocket_not_0(roll)
        self.session.update_bankroll(win, dozens=True)
        return win

    def setup(self): 
        pass 

    def on_win(self): 
        pass

    def on_loss(self):
        pass

    def cleanup(self):
        self.session.check_and_handle_insufficient_funds()

    def execute(self, roll):
        self.setup()
        if self.session.round == 1:
            self.session.history['bets'].append(self.session.curr_bet)

        win = self.even_odds_strat(roll) if not self.use_dozens else self.dozens_strat(roll)
        if win: 
            self.on_win()
        else: 
            self.on_loss()
        
        self.cleanup()


# Bet on red every time
class AlwaysRed(BettingStrategy):
    pass

# Bet on the 2 dozens that weren't rolled last time
class Irfans(BettingStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        self.use_dozens = True

    @staticmethod
    def get_dozen(n): 
        if n > 0 and n <= 12: return 1
        if n > 12 and n <= 24: return 2
        if n > 24 and n <= 36: return 3

    @staticmethod
    def pocket_not_0(roll): 
        return roll['pocket'] != 0 and roll['pocket'] != -1

    @staticmethod
    def last_roll(self):
        return self.history['rolls'][-1][0] if self.history['rolls'] else 1

# Bet double after every loss, reset after every win
class Martingale(BettingStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)

    def on_win(self):
        self.session.reset_bet()

    def on_loss(self):
        self.session.curr_bet *= 2

# Bet double + 1 unit after every loss, reset after every win
class GrandMartingale(Martingale):
    def __init__(self, session_instance):
        super().__init__(session_instance)

    def on_loss(self):
        super().on_loss()
        self.session.curr_bet += self.session.bet_unit

# Increase bet by 1 unit after a win and decrease by 1 unit after a loss
class Dalembert(BettingStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)

    def on_win(self):
        self.session.curr_bet += self.session.bet_unit 

    def on_loss(self):
        if self.session.curr_bet > self.session.bet_unit:
            self.session.curr_bet -= self.session.bet_unit

# Increase bets by 1 unit on win, reset on loss or after 3 wins in a row
class Paroli(BettingStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        self.streak = 0

    def reset_streak(self):
        self.session.reset_bet()
        self.streak = 0

    def on_win(self):
        self.session.curr_bet *= 2
        self.streak += 1
        if self.streak == 3:
            self.reset_streak()

    def on_loss(self):
        self.reset_streak()

#FIXME: this strategy is completely wrong
# https://www.roulette17.com/systems/hollandish/
class Hollandish(BettingStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        self.streak = 0

    def on_win(self):
        self.streak -= 1 if self.streak else 0
        if self.streak == 0: 
            self.session.curr_bet += 2 * self.session.bet_unit

    def on_loss(self):
        self.streak += 1

# FIXME: I AM PROBABLY WRONG
# A simpler version of this: https://www.888casino.com/blog/tier-et-tout
class TierEtTout(BettingStrategy):
    def __init__(self, session_instance): 
        super().__init__(session_instance)
        self.session.curr_bet = self.session.bet_unit * 3
        
    def setup(self): 
         self.session.bet_unit = math.ceil(1/9 * self.session.bankroll)

    def on_win(self):
        self.session.curr_bet = self.session.bet_unit * 3
        
    def on_loss(self):
        self.session.curr_bet = self.session.bet_unit * 6

# General class for progression strategies
class ProgressionStrategy(BettingStrategy):
    def __init__(self, session_instance, progression):
        super().__init__(session_instance)
        self.session.curr_bet = progression[0] * self.session.bet_unit if isinstance(progression[0], (int, float)) else None
        self.progression = progression
        self.streak = 0

    def on_win(self): 
        self.streak = self.streak + 1 if self.streak < len(self.progression)-1 else 0

    def on_loss(self):
        self.streak = 0

    def cleanup(self):
        self.session.curr_bet = self.progression[self.streak] * self.session.bet_unit
        super().cleanup()

# The classic 1-3-2-6 baccarat and roulette progression
class OneThreeTwoSix(ProgressionStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance, [1, 3, 2, 6])

# The most optimal progression for doubling your money according to `progressions_sim.py`
class OneFourEight(ProgressionStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance, [1, 4, 8])

# Losing moves you up the fibonacci sequence, winning moves you down 2 steps
class Fibonacci(ProgressionStrategy):
    def __init__(self, session_instance):
        progression = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
        super().__init__(session_instance, progression)
        self.streak = 0

    def on_win(self):
        self.streak = self.streak - 2 if self.streak >= 2 else 0

    def on_loss(self):
        self.streak += 1 

# 2,1,2 progression; when you complete the sequence you raise the bet by 1 until you lose
class Manhattan(ProgressionStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance, [2, 1, 2])
        self.pointer = 0

    def on_win(self):
        self.pointer += 1
        if self.pointer >= len(self.progression):
            self.streak += 1
            self.pointer = 0

    def on_loss(self):
            self.streak, self.pointer = (0, 0)

    def cleanup(self):
        self.session.curr_bet = (self.progression[self.pointer] + self.streak) * self.session.bet_unit
        self.session.check_and_handle_insufficient_funds()

# https://www.roulette17.com/systems/guetting/
class GuettingProgressionStrategy(ProgressionStrategy):
    def __init__(self, session_instance, progression):
        super().__init__(session_instance, progression)
        self.session.curr_bet = progression[0][0] * self.session.bet_unit
        self.level = 0
        self.pointer = 0

    def move_next_lvl_or_stage(self):
        self.streak = 0
        # move within level
        if self.pointer < len(self.progression[self.level])-1:
            self.pointer += 1
        # move to next level
        elif self.level < len(self.progression)-1:
            self.level += 1
            self.pointer = 0
        # progression complete, reset
        else:
            self.level = 0
            self.pointer = 0

    def on_win(self):
        if self.streak == 0: 
            self.streak += 1  # have to win twice to move up
        else: 
            self.move_next_lvl_or_stage()

    def on_loss(self):
        if self.streak == 0: 
            self.level -= 1 if self.level > 0 else 0 # go down a level
            self.pointer = 0
        else: 
            self.streak = 0 # have to lose twice to move down

    def cleanup(self):
        self.session.curr_bet = self.progression[self.level][self.pointer] * self.session.bet_unit
        super().cleanup()

# The standard guetting progression 
class StandardGuetting(GuettingProgressionStrategy):
    def __init__(self, session_instance):
        levels = [[1], [1.5, 2, 3], [4, 6, 8], [10, 15, 20]]
        super().__init__(session_instance, progression=levels)

# A guetting progression optimised for doubling your money according to progressions_sim.py
class OptimalGuetting(GuettingProgressionStrategy):
    def __init__(self, session_instance):
        levels = [[1], [10, 4, 1], [2, 1, 8], [2, 3, 6], [4, 7, 4]]
        super().__init__(session_instance, progression=levels)

# Standard labouchere progression w/ lenght based on profit goal 
class Labouchere(BettingStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        units_to_make = math.ceil((self.session.profit_goal - self.session.bankroll) / self.session.bet_unit)
        self.set_progression(units_to_make)
        self.handle_round()

    def set_progression(self, units_to_make):
        self.progression = self.get_unit_distribution(units_to_make)

    def handle_round(self):
        self.set_round_units()
        self.session.curr_bet = self.round_units * self.session.bet_unit
        self.session.history['progression'].append(self.progression.copy())

    def get_unit_distribution(self, units_to_make):
        units = 1
        sequence_sum = 0
        sequence = []

        while sequence_sum < units_to_make:
            sequence.append(units)
            sequence_sum += units
            units += 1

        if sequence_sum > units_to_make:
            remainder = sequence_sum - units_to_make
            sequence[-1] -= remainder

        return sequence

    def set_round_units(self):
        if not self.progression: 
            Exception("Progression is empty")
        elif len(self.progression) == 1: 
            self.round_units = self.progression[0]
        else:
            self.round_units = self.progression[0] + self.progression[-1]

    def on_win(self):
        self.progression = self.progression[1:-1] # remove first and last elements
    
    def on_loss(self):
        self.progression.append(self.round_units) # add the loss to the end of the progression

    def cleanup(self):
        self.handle_round()
        super().cleanup()

# https://www.roulettelife.com/index.php?topic=9.0
class JohnsonProgression(Labouchere):
    def __init__(self, session_instance):
        super().__init__(session_instance)

    def set_progression(self, units_to_make):
        progression_len = self.session.min_rounds or units_to_make
        self.progression = [1] * progression_len

    def distribute_losses(self, to_distribute):
        while to_distribute > 0:
            if not self.progression:
                break
            min_index = self.progression.index(min(self.progression))
            self.progression[min_index] += 1
            to_distribute -= 1

    def on_loss(self):
        if not self.use_dozens: 
            self.distribute_losses(self.round_units)
        else: 
            self.distribute_losses(self.round_units*2)

    # ==============================
    # ------ MISC STRATEGIES -------
    # ==============================
class RouletteStrategy(ABC):
    def __init__(self, session_instance):
        self.session = session_instance
        self.use_dozens = False

    def units_gained(self, units):
        self.session.bankroll += units * self.session.bet_unit
        self.session.history['wl'].append('win')
    
    def units_lost(self, units):
        self.session.bankroll -= units * self.session.bet_unit
        self.session.history['wl'].append('lose')

    @abstractmethod
    def execute(self, roll):
        pass

# https://www.888casino.com/blog/kavouras-bet
class Kavouras(RouletteStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        self.session.curr_bet = self.session.bet_unit * 8

    def execute(self, roll):
        if roll['pocket'] in range(0, 4): 
            self.units_gained(1)
        else: 
            self.units_lost(1)

        # double street
        if roll['pocket'] in range(31, 37):
            self.units_gained(4)
        else: 
            self.units_lost(2)

        # splits
        splits = list(range(8, 12)) + list(range(15, 19)) + list(range(17, 21)) + list(range(27, 31))
        if roll['pocket'] in splits:
            self.units_gained(10)
        else:
            self.units_lost(5)

# https://www.888casino.com/blog/4-pillars-system-notes-madman
class FourPillars(RouletteStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        self.session.curr_bet = self.session.bet_unit * 6

    def execute(self, roll):
        if roll['pocket'] in range(4, 10) or roll['pocket'] in range(25, 31):
            self.units_lost(1) # when you win you still lose? 
        else: 
            self.units_lost(2)

        if roll['pocket'] in [19, 20, 22, 23, 31, 32, 34, 35]:
            self.units_gained(3)
        else: 
            self.units_lost(2)
            
        if roll['pocket'] in [14, 15, 17, 18]:
            self.units_gained(12)
        else: 
            self.units_lost(2)

# https://www.playojo.com/blog/roulette/best-roulette-strategy/
class SixSixSix(RouletteStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        self.session.bet_unit = 0.1 * self.session.bet_unit 
        self.session.curr_bet = self.session.bet_unit * 66

    def execute(self, roll):
        pocket, color = (roll['pocket'], roll['color'])
        splits = [0, 2, 8, 11, 10, 13, 17, 20, 26, 29, 28, 31]
        singles = [4, 6, 15]
        
        if color == 'Red': 
            self.units_gained(36)
        else: 
            self.units_lost(36)

        if pocket in splits:
            self.units_gained(48)
        else: 
            self.units_lost(24)

        if pocket in singles: 
            self.units_gained(66)
        else: 
            self.units_lost(6)

# https://www.888casino.com/blog/positional-roulette#how-to-play-positional-roulette
class PositionalRoulette(RouletteStrategy):
    def __init__(self, session_instance):
        super().__init__(session_instance)
        self.session.curr_bet = self.session.bet_unit * 8
        self.roulette = self.session.game.roulette

    def find_positional_numbers(self):
        all_n = set(range(1, 37))
        appeared_n = set(roll[0] for roll in self.session.history['rolls'])
        uncommon_n = all_n - appeared_n

        prev_pocket, prev_color = self.session.history["rolls"][-1]
        if prev_color == "Green": prev_color = "Red"
        selected_pockets = []

        def get_next_pocket_index(index):
            return (index + 1) % len(self.roulette)

        def get_prev_pocket_index(index):
            return (index - 1) % len(self.roulette)
        
        cycle_count = 0
        i = get_next_pocket_index(prev_pocket)
        while len(selected_pockets) < 8:
            n, color = self.roulette[i]
            if color == prev_color and n not in selected_pockets and n not in uncommon_n:
                selected_pockets.append(n)
            else:
                cycle_count += 1

            if cycle_count >= len(self.roulette):
                break  # If we've gone through all pockets without finding new ones, break out of the loop

            if len(selected_pockets) < 4: 
                i = get_next_pocket_index(i) # find next 4 numbers
            else:
                i = get_prev_pocket_index(i) # find previous 4 numbers
        return selected_pockets

    def execute(self, roll):
        if self.session.round < 38:
            pass # build data on uncommon numbers
        else:
            winning_pockets = self.find_positional_numbers() # bet on 8 numbers
            if roll["pocket"] in winning_pockets:
                self.units_gained(35 - len(winning_pockets)-1)
            else: 
                self.units_lost(len(winning_pockets))