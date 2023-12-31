# Roulette simulation

A simple framework for testing different betting strategies on a roulette table. Usual simulators test a strategy over million if not billions of games, until the bankroll reaches 0. This simulator only concerns itself to test a strategy in real life conditions. That is, if I enter a casino
with X amount of money, what is the probability that I will leave with an amount Y of money by using a certain strategy.

It is obviously impossible to create a strategy that edges the house, but by using a strategy focusing on short-term gains, it should be possible to increase the probability of leaving the casino with a profit, as long as the player is willing to leave the table as soon as the profit is made.

## Requirements

- Python 3.6+
- `pip install -r requirements.txt`

## Currently implemented strategies

Many popular even money strategies are implemented, such as:

- Bet on red
- Martingale and Grand Martingale
- Paroli
- D'Alembert
- Tier et Tout
- Labouchere
- Fibonacci
- Johnson progression
- Guetting
- 1326
- Manhattan

These strategies are applied to default on roulette red/black odds, but the odds can be changed to Banker/Player in Baccarat, or even Blackjack.
Additionally, every strategy can optionally be used to bet on dozes by using it in conjunction with `Irfans`'s strategy.

Other roulette-only strategies are also available:

- Kavouras
- Four pillars
- 666
- Positional roulette

## What is Irfan's strategy?

Irfan's strategy involves betting on 2 out of the 3 dozens. The 2 dozens chosen are the ones that did not appear in the last spin. If a loss in incurred, the bet is repeated on the same 2 dozens. Variations such as `irfans_with_martingale` and `irfans_with_paroli` are also available and follow the aforementioned strategies with the addition of Martingale or Paroli respectively.

## Progession simulator

TODO:

## Usage

To run the simulation with a wizard interface, run:

```python
python3 cli.py
```

Options such as using an american roulette and custom simulation amount are only available programmatically, by modifying `main.py` and running:

```python
python3 main.py
```

## Implement custom strategies

To add strategies, add a method in `strategies.py`, and add the method name to the `strategies` dictionary at the end of the file.
