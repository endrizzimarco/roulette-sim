import random
import statistics

class Progression:
    def __init__(self, progression):
        self.bankroll = 80
        self.aim = 160
        self.bet_unit = 2.5 
        self.curr_bet = 2.5
        self.streak = 0
        self.progression = progression

    # simple progression with 1,2,4,6
    def execute(self):
        simulations = 2**10
        successful = 0
        
        for _ in range(simulations):
            while self.bankroll < self.aim and self.bankroll > 0 and self.curr_bet <= self.bankroll:
                roll = random.choices(["Red", "Black", "Green"], weights=[18/37, 18/37, 1/37])
                win = roll == ["Red"]
                self.update_bankroll(win)
                # print(self.bankroll)
                if win:
                    self.streak += 1
                    if self.streak < len(self.progression):
                        self.curr_bet = self.progression[self.streak] * self.bet_unit
                    else:
                        self.streak = 0
                else:
                    self.curr_bet = self.bet_unit
                    self.streak = 0 

            if self.bankroll >= self.aim:
                successful += 1

            self.reset()
        
        success_rate = successful / simulations * 100
        return success_rate

    def update_bankroll(self, win):
        if win:
            self.bankroll += self.curr_bet
        else:
            self.bankroll -= self.curr_bet 

    def reset(self):
        self.bankroll = 50
        self.aim = 100
        self.bet_unit = 2.5 
        self.curr_bet = 2.5
        self.streak = 0
        

def random_sequence(M, N, x):
    if x > N - M + 1:
        raise ValueError("The number of elements in the sequence (x) is larger than the range (M to N).")
    
    # Create a list of numbers from M to N (inclusive)
    numbers_range = list(range(M, N + 1))
    # Generate a random sequence of x elements from the range
    random_sequence = random.sample(numbers_range, x)

    return random_sequence

def test_random_progressions():
    N = 8
    M = 4
    best_success_rate = 0
    best_progression = []

    for _ in range(2**14):
        x = random.randint(1, 2)
        progression = [1] + [random.randint(1, 4)] +  random_sequence(M, N, x)
        # print(f"Testing progression: {progression}")
        strat = Progression(progression)
        success_rate = strat.execute()
        if success_rate > best_success_rate:
            results = []
            for _ in range(10):
                results.append(strat.execute())
            # remove stinky outliers    
            results.remove(max(results))
            results.remove(min(results)) 
            # take the average of the remaining 8 results
            average = sum(results) / len(results)
            if average > best_success_rate:
                best_success_rate = average
                best_progression = progression
                print(f"New best success rate: {best_success_rate}% with progression: {best_progression}")

    print(f"Best success rate: {best_success_rate}% with progression: {best_progression}")


def find_best_progressions(good_progressions):
    best_success_rate = 0
    best_progression = []

    for progression in good_progressions:
        strat = Progression(progression)
        results = []
        for _ in range(100):
            results.append(strat.execute())
        median = statistics.median(results)
        if median > best_success_rate:
            best_success_rate = median
            best_progression = progression
            print(f"New best success rate: {best_success_rate}% with progression: {best_progression}")
            

good_progressions = [[1, 1, 4, 8], [1, 4, 8, 6], [1, 4, 8], [1, 4, 7], [1, 2, 4], [1, 3, 6]]
# find_best_progressions(good_progressions)
test_random_progressions()