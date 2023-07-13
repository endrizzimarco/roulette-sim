from InquirerPy import prompt
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.validator import EmptyInputValidator
from strategies import Strategy
from prettytable import PrettyTable

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
        "message": "Select the betting strategy",
        "type": "rawlist",
        "choices": list(Strategy().strategies.keys()) + ["all"],
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
  simulations = 2**13 # 8192
  reached_session_aim = 0
  for _ in range(simulations):
    strategy = Strategy(bankroll=int(result[0]), bet=float(result[1]), session_aim=int(result[2]))
    results = strategy.execute(strat)
    if max(results) >= strategy.session_aim: 
      reached_session_aim += 1
  return(reached_session_aim/simulations * 100)


if result[3] == "all":
  cols = Strategy().strategies.keys()
  row = []
  table = PrettyTable(cols)
  for strat in cols:
    row.append(simulate(result, strat))
  table.add_row(row)
  print(table)
else: 
  chance = simulate(result, result[3])
  print(f"Win probability for a session: {chance}%")