from strategies import *
import random
import copy


class Game:
    BACCARAT_ODDS = [50.68, 49.32] # [banker (no, viz), player]
    BLACKJACK_ODDS = [49.75, 50.25] # [strategy, no_strategy]
    BLACKJACK_NO_STRATEGY_ODDS = [49.00, 51.00] # [strategy, no_strategy]
    def __init__(self, game):
        self.ROULETTE = [(0, 'Green'), (1, 'Red'), (2, 'Black'), (3, 'Red'), (4, 'Black'), (5, 'Red'),(6, 'Black'), (7, 'Red'), (8, 'Black'), (9, 'Red'), (10, 'Black'), (11, 'Black'), (12, 'Red'), (13, 'Black'), (14, 'Red'), (15, 'Black'), (16, 'Red'), (17, 'Black'), (18, 'Red'), (19, 'Red'), (20, 'Black'), (21, 'Red'), (22, 'Black'), (23, 'Red'), (24, 'Black'), (25, 'Red'), (26, 'Black'), (27, 'Red'), (28, 'Black'), (29, 'Black'), (30, 'Red'), (31, 'Black'), (32, 'Red'), (33, 'Black'), (34, 'Red'), (35, 'Black'), (36, 'Red'),]
        if game == 'roulette_american':
            self.ROULETTE += [(-1, 'Green')]
        self.type = game

    def roll(self):
        if self.type.startswith('baccarat'):
            weights = self.BACCARAT_ODDS
            if self.type == 'baccarat_player':
                weights = weights[::-1]
        elif self.type.startswith('blackjack'):
            weights = self.BLACKJACK_ODDS if not self.type == 'blackjack_no_strategy' else self.BLACKJACK_NO_STRATEGY_ODDS
        else: 
            return random.choice(self.ROULETTE)

        return (None, random.choices(['Red', 'Black'], weights=weights)[0])



class CasinoSession: 
    def __init__(self, strategy='always_red', bankroll=100, bet_unit=2.5, profit_goal=250, min_rounds=0, max_rounds=0, table_limits=0, game='roulette_european'):
        self.bankroll = bankroll
        self.bet_unit = bet_unit
        self.curr_bet = bet_unit
        self.min_rounds = min_rounds
        self.max_rounds = max_rounds
        self.table_limits = table_limits
        self.profit_goal = profit_goal if profit_goal else float('inf')

        # meta
        self.game = Game(game)
        self.history = {'bankroll': [bankroll], 'bets': [], 'rolls': [], 'progression': [], 'wl': []}
        self.round = 1

        # strategies
        self.strategies = {
            'always_red': AlwaysRed, 
            'irfans': Irfans,
            'martingale': Martingale,
            'grand_martingale': GrandMartingale,
            'piquemouche': Piquemouche,
            'dalembert': Dalembert,
            'paroli': Paroli,
            'fibonacci': Fibonacci,
            'hollandish': StandardHollandish,
            'tier_et_tout': TierEtTout,
            '1326': OneThreeTwoSix,
            '148': OneFourEight,
            'manhattan': Manhattan,
            'two_up_two_down': TwoUpTwoDown,
            'standard_guetting': StandardGuetting,
            'optimal_guetting': OptimalGuetting,
            'labouchere': Labouchere,
            'reverse_labouchere': ReverseLabouchere,
            'johnson_progression': JohnsonProgression,
            'kavouras': Kavouras,
            'four_pillars': FourPillars,
            'sixsixsix': SixSixSix,
            'positional_roulette': PositionalRoulette,
        }
        self.strategy = self.strategies[strategy](self)

    def simulate(self):
        while self.should_continue(self.strategy):
            self.tick()
        return self.history

    def tick(self, win=None):
        if self.should_continue(self.strategy):
            roll = self.game.roll()
            if win is not None: 
                self.strategy.execute(override=win)
            else:
                self.strategy.execute({"pocket": roll[0], "color": roll[1]})
            self.update_history(roll)
            self.round += 1
        return self

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
            self.bankroll += self.curr_bet if not self.game.type == 'baccarat_banker' else 0.95 * self.curr_bet
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
        if self.table_limits and self.curr_bet > self.table_limits:
            self.curr_bet = self.table_limits
        elif self.curr_bet > self.bankroll:
            self.curr_bet = self.bankroll


def update_history(history, session):
    history["bankrolls"].append(session["bankroll"])
    history["bets"].append(session["bets"])
    history["wl"].append(session["wl"])
    history["progressions"].append(session["progression"])

def simulate(params, continue_session=None):
    sim_history = {
        "bankrolls": [],
        "bets": [], 
        "success_rate": 0, 
        "wl": [],
        "progressions": []
    }

    # Execute every session sequentially
    for _ in range(params["sessions"]):
        session = CasinoSession(**params["data"]) if not continue_session else copy.deepcopy(continue_session)
        simulation = session.simulate()
        update_history(sim_history, simulation)


    # Calculate success rate
    won_sessions = sum(session[-1] >= params["data"]["profit_goal"] for session in sim_history["bankrolls"])
    sim_history["success_rate"] = won_sessions / params["sessions"] * 100

    return sim_history


def find_optimal_bet_size(params):
    best_bet = 0
    best_chance = 0
    bankroll = params["data"]["bankroll"]
    for bet in range(int(bankroll/4), int(bankroll/2)): #FIXME: this is shit!
        params["data"]["bet_unit"] = bet
        chance = simulate(params)["success_rate"]
        if chance > best_chance: 
            best_bet = bet 
            best_chance = chance
            # print(f"({strat}) New best bet: {best_bet}, with chance {chance}%")
    return (best_bet, best_chance)

def optimise(params, optimise_bet=False, win_chance=0):
    strategies = []
    chances = []
    bets = []

    for strategy in CasinoSession().strategies.keys():
        params["strat"] = strategy
        chance = simulate(params)["success_rate"]
        if optimise_bet: 
            bet, chance = find_optimal_bet_size(params)
        if win_chance and chance <= win_chance:
            continue
        strategies.append(strategy)
        chances.append(f"{chance:.4f}%")
        if optimise_bet: bets.append(bet)

    if win_chance and not chances: 
        params["data"]["profit_goal"] -= params["data"]["profit_goal"] * 0.1
        print(f"changing session aim to: {params['data']['profit_goal']}")
        return optimise(params, optimise_bet=optimise_bet, win_chance=win_chance)

    if optimise_bet: 
        result = sorted(zip(strategies, bets, chances), key=lambda x: x[2], reverse=True)
    else:
        result = sorted(zip(strategies, chances), key=lambda x: x[1], reverse=True)
        
    return result[:10] if not win_chance else (params["data"]["profit_goal"], result[:5])