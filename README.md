# Roulette simulation

A simple framework for testing different betting strategies on a roulette table. Usual simulators test a strategy over million if not billions of games, until the bankroll reaches 0. This simulator only concerns itself to test a strategy in real life conditions. That is, if I enter a casino
with X amount of money, what is the probability that I will leave with an amount Y of money by using a certain strategy.

It is obviously impossible to create a strategy that edges the house, but by using a strategy focusing on short-term gains, it should be possible to increase the probability of leaving the casino with a profit, as long as the player is willing to leave the table as soon as the profit is made.

## Requirements

- Python 3.6+
- `pip install -r requirements.txt`

## Currently implemented strategies

- Always bet on red
- Martingale
- Irfan's strategy

## Usage

To run the simulation with a wizard interface, run:

```python
python3 cli.py
```

Options such as using an american roulette and custom simulation amount are only available programmatically, by modifying `main.py` and running:

```python
python3 main.py
```

## Add strategies

To add strategies, add a method in `strategies.py`, and add the method name to the `strategies` dictionary at the end of the file.
