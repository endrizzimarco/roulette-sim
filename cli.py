from InquirerPy import prompt
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.validator import EmptyInputValidator
from simulate import CasinoSession

# TODO: support baccarat and blackjack odds
questions = [
    {
        "message": "Bankroll amount?",
        "type": "input",
        "validate": EmptyInputValidator(),
        "default": "50"
    },
    {
        "message": "Bet amount?",
        "type": "input",
        "validate": EmptyInputValidator(),
        "default": "2.5"
    },
    {
        "message": "Session aim?",
        "type": "input",
        "validate": EmptyInputValidator(),
        "default": "100"
    },
    {
        "message": "Select the betting strategy:",
        "type": "list",
        "choices": ["all"] + list(CasinoSession().strategies.keys()),
        "pointer": INQUIRERPY_POINTER_SEQUENCE,
    },
]

result = prompt(
    questions,
    style={"questionmark": "#ff9d00 bold"},
    vi_mode=True,
    style_override=False,
)


def simulate(result, strat):
  simulations = 2**16 # 16384
  reached_session_aim = 0
  for _ in range(simulations):
    strategy = CasinoSession(strategy=strat, bankroll=float(result[0]), bet_unit=float(result[1]), profit_goal=float(result[2]))
    results = strategy.simulate()
    if max(results["bankroll"]) >= strategy.profit_goal: 
      reached_session_aim += 1
  return(reached_session_aim/simulations * 100)


if result[3] == "all":
  for strat in CasinoSession().strategies.keys():
    print(f'{strat}: {simulate(result, strat)}%')
else: 
  chance = simulate(result, result[3])
  print(f"Win probability for a session: {chance}%")