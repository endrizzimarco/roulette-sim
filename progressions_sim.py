import random
import statistics


class Progression:
    def __init__(self, strategy, progression):
        self.progression = progression() if callable(progression) else progression
        self.strategies = {"standard": self.standard_progression, "guetting": self.guetting}
        self.strategy = self.strategies[strategy]
        self.bankroll = 100
        self.aim = 200
        self.bet_unit = 2.5 
        self.curr_bet = 2.5
        self.streak = 0
        self.pointer = 0
        self.level = 0
        self.lvls = self.progression


    def execute(self):
        simulations = 2**10
        successful = 0
        
        for _ in range(simulations):
            while self.bankroll < self.aim and self.bankroll > 0 and self.curr_bet <= self.bankroll:
                roll = random.choices(["Red", "Black", "Green"], weights=[18/37, 18/37, 1/37])
                win = roll == ["Red"]
                self.update_bankroll(win)
                # print(self.bankroll)
                self.strategy(win)

            if self.bankroll >= self.aim: successful += 1
            self.reset()

        return successful / simulations * 100
    
    def standard_progression(self, win):
        if win:
            self.streak += 1
            if self.streak < len(self.progression):
                self.curr_bet = self.progression[self.streak] * self.bet_unit
                self.reset_if_insufficent_funds()
            else:
                self.streak = 0
        else:
            self.reset_bet()

    def guetting(self, win):
        if win: 
            if self.streak == 0: 
                self.streak += 1  # repeat last bet
            else: 
                move_next_lvl_or_stage(self)
                self.curr_bet = self.lvls[self.level][self.pointer] * self.bet_unit
                self.reset_if_insufficent_funds()
        else: 
            if self.streak == 0: 
                self.level -= 1 if self.level > 0 else 0 # go down a level
                self.pointer = 0
                self.curr_bet = self.lvls[self.level][self.pointer] * self.bet_unit
                self.reset_if_insufficent_funds()
            else: 
                self.streak = 0 # repeat last bet 

    def update_bankroll(self, win):
        if win:
            self.bankroll += self.curr_bet
        else:
            self.bankroll -= self.curr_bet 

    def reset_bet(self):
        self.curr_bet = self.bet_unit
        self.streak = 0

    def reset_if_insufficent_funds(self):
        if self.curr_bet > self.bankroll:
            self.curr_bet = self.bankroll
            self.streak, self.level, self.pointer = 0, 0, 0

    def reset(self):
        self.bankroll = 50
        self.aim = 100
        self.bet_unit = 2.5 
        self.curr_bet = 2.5
        self.streak = 0

def move_next_lvl_or_stage(self):
    self.streak = 0
    if self.level == 0: # move up within level
        self.level += 1
    elif self.pointer < 2: # move up within stage
        self.pointer += 1
    elif self.level < len(self.lvls)-1: # move up within level
        self.level += 1

def random_sequence(n, m, x, sort=False, starts=[]):
    if x > m - n + 1:
        raise ValueError("The number of elements in the sequence (x) is larger than the range (M to N).")
    # Create a list of numbers from M to N (inclusive)
    numbers_range = list(range(n, m + 1))
    # Generate a random sequence of x elements from the range
    random_sequence = random.sample(numbers_range, x)
    if sort: 
        random_sequence.sort()

    return random_sequence if not starts else starts + random_sequence

def test_random_combinations(type, progression):
    best_success_rate = 0
    best_progression = []

    for _ in range(2**14):
        # print(f"Testing progression: {progression}")
        strat = Progression(type, progression)
        success_rate = strat.execute()
        if success_rate > best_success_rate:
            results = []
            for _ in range(20):
                results.append(strat.execute())
            # remove stinky outliers    
            results.remove(max(results))
            results.remove(min(results)) 
            # take the average of the remaining 8 results
            average = sum(results) / len(results)
            if average > best_success_rate:
                best_success_rate = average
                best_progression = strat.progression
                print(f"New best success rate: {best_success_rate}% with progression: {strat.progression}")

    print(f"Best success rate: {best_success_rate}% with progression: {best_progression}")


def find_best_progressions(type, good_progressions):
    best_success_rate = 0
    best_progression = []

    for progression in good_progressions:
        strat = Progression(type, progression)
        results = []
        for _ in range(100):
            results.append(strat.execute())
        median = statistics.median(results)
        if median > best_success_rate:
            best_success_rate = median
            best_progression = progression
            print(f"New best success rate: {best_success_rate}% with progression: {best_progression}")


progression_type = "guetting" # {standard, guetting, labouchere}
n, m = (1, 10)

# test random progressions
standard_progression = lambda: [1] + [random.randint(1, 4)] + random_sequence(n, m, 2)
guetting_progression = lambda: [[1], random_sequence(n, m, 1, starts=[10, 10]), [2, 1, 8], [2, 3, 6], random_sequence(n, m, 2, starts=[4])]

# test good progressions
standard_good_progressions = [[1, 1, 4, 8], [1, 4, 8, 6], [1, 4, 8], [1, 4, 8, 3], [1, 4, 7], [1, 2, 4], [1, 3, 6], [1, 4, 7, 5], [1, 3, 6, 8]]
guetting_good_progressions = [
    [[1], [8, 3, 5], [2, 1, 8], [3, 6, 5], [7, 6, 4]],
    [[1], [8, 5, 1], [5, 3, 1], [2, 1, 6], [1, 7, 8]],
    [[1], [8, 3, 5], [2, 1, 8], [7, 8, 2], [4, 8, 5]],
    [[1], [8, 3, 5], [2, 1, 8], [2, 3, 6], [4, 8, 5]],
    [[1], [8, 4, 6], [2, 1, 8], [2, 3, 6], [4, 4, 6]],
    [[1], [8, 5, 4], [2, 1, 8], [2, 3, 6], [4, 4, 3]],
    [[1], [10, 4, 1], [2, 1, 8], [2, 3, 6], [4, 7, 4]],
    [[1], [10, 4, 1], [2, 1, 8], [2, 3, 6], [4, 6, 10]],
    [[1], [10, 10, 9], [2, 1, 8], [2, 3, 6], [4, 4, 6]],
    [[1], [10, 10, 6], [2, 1, 8], [2, 3, 6], [4, 1, 2]]

]

# test_random_combinations(progression_type, globals()[f"{progression_type}_progression"])
find_best_progressions(progression_type, globals()[f"{progression_type}_good_progressions"] )