# Dice Game Simulation Using Q-Learning

## Overview

This project implements a Dice Game simulation where decision-making is modeled using Q-Learning, a type of reinforcement learning. The simulation aims to optimize strategies over numerous games, learning to maximize rewards based on the game's outcomes. Players roll dice and accumulate scores, aiming to reach a designated score range without exceeding a maximum score limit.

## Features

- **Q-Learning**: Leverages Q-Learning to optimize dice selection strategies based on past game outcomes.
- **Dynamic Decision Making**: Adjusts strategies dynamically based on current game state, utilizing learned values from previous games.
- **Configurable Game Parameters**: Supports customization of game settings such as number of dice sides, number of dice, and score thresholds.
- **Verbose Debugging**: Offers a verbose mode for detailed logging of the game's internal state and decision-making process.

## Requirements

- Python 3.8 or higher

## Installation

The project utilizes Python's built-in libraries and does not require external dependencies beyond `colorama` for colored console output.

To install `colorama`, run:

```bash
pip install colorama
```

No additional installation steps are required other than having a Python interpreter. Simply clone the repository or download the source code to get started.

## Usage

To run the simulation, use the following command format:

```bash
python dice_game_simulation.py -NS <number_of_sides> -ND <number_of_dice> -H <high_score> -L <low_score> -G <number_of_games> -M <exploration_parameter> [-v]
```

- `-NS <number_of_sides>`: Specifies the number of sides on each die.
- `-ND <number_of_dice>`: Sets the maximum number of dice that can be rolled in one turn.
- `-H <high_score>`: Defines the upper score limit that must not be exceeded.
- `-L <low_score>`: Sets the lower score threshold needed to potentially win.
- `-G <number_of_games>`: Determines how many games to simulate.
- `-M <exploration_parameter>`: Sets the exploration parameter for Q-Learning.
- `-v`: Enables verbose mode for detailed debug output.

## Example Usage

```bash
python dice_game_simulation.py -NS 6 -ND 2 -H 21 -L 15 -G 1000 -M 10 -v
```

## Output

The simulation outputs the play made by each player, intermediate scores, and final results of each game based on the scores. When verbose mode is enabled, detailed logs of the Q-Learning algorithm including each decision and state update are shown.

## Implementation Details

The simulation is structured into two main components:

- **DiceGame Class**: Handles the mechanics of playing a dice game, such as rolling dice, updating q-learning tables and determining game outcomes.
- **QLearning Class**: Implements the Q-Learning algorithm, deciding how many dice to roll at each turn based on past experiences to optimize the chance of winning.
- **Main Module**: Orchestrates the simulation setup, execution, and logging based on user-defined parameters.