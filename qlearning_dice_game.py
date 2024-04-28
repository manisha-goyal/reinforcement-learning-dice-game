import argparse
import random
from colorama import init, Fore

init(autoreset=True)
verbose = False

class QLearning:
    def __init__(self, num_dice, exploration_param):
        self.num_dice = num_dice
        self.exploration_param = exploration_param
        self.wins = {}
        self.losses = {}

    def choose_number_of_dice(self, current_score, opponent_score):
        weighted_probs = [1 / self.num_dice] * self.num_dice # Initialize to equal probability assuming no games played yet
        win_probs = []
        total_games = 0
        win_values = ""
        loss_values = ""

        print_debug(f"\nState = [{current_score}, {opponent_score}]")

        # Compute win probabilities of current state for each dice option
        for num_dice in range(1, self.num_dice + 1):
            win = self.wins.get((current_score, opponent_score, num_dice), 0)
            loss = self.losses.get((current_score, opponent_score, num_dice), 0)
            total = win + loss

            w_d = win / total if total > 0 else 0
            win_probs.append(w_d)
            total_games += total

            win_values += f"Wins[{current_score}, {opponent_score}, {num_dice}] = {win}, "
            loss_values += f"Losses[{current_score}, {opponent_score}, {num_dice}] = {loss}, "

        win_values = win_values.rstrip(', ')
        loss_values = loss_values.rstrip(', ')
        print_debug(win_values)
        print_debug(loss_values)

        # Compute weighted probabilities of current state for each dice option
        if total_games > 0:
            # Find the best d (break tie randomly) and Wd
            best_d = random.choice([i for i, w in enumerate(win_probs) if w == max(win_probs)])
            w_prime_d = win_probs[best_d]

            # Calculate Pd for Wd
            p_d = (total_games * w_prime_d + self.exploration_param) / (total_games * w_prime_d + self.num_dice * self.exploration_param)
            
            # Calculate P'd for W'd
            weighted_probs = []
            s = sum(win_probs) - w_prime_d
            for i, w_d in enumerate(win_probs):
                if i == best_d:
                    weighted_probs.append(p_d)
                else:
                    p_prime_d = (1 - p_d) * (w_d + self.exploration_param) / (s * total_games + (self.num_dice - 1) * self.exploration_param)
                    weighted_probs.append(p_prime_d)

        print_debug(f"Win Probabilities = [{', '.join(str(round(p, 3)) for p in win_probs)}]")
        print_debug(f"Weighted probabilities = [{', '.join(str(round(p, 3)) for p in weighted_probs)}]")

        # Choose a dice number randomly based on the weighted probabilities
        return random.choices(range(1, self.num_dice + 1), weights=weighted_probs, k=1)[0]

    def update_training_tables(self, winner_history, loser_history):
        # Update wins table with winner's history
        for state in winner_history:
            self.wins[state] = self.wins.get(state, 0) + 1

        # Update losses table with loser's history
        for state in loser_history:
            self.losses[state] = self.losses.get(state, 0) + 1

    def print_debug_training_tables(self):
        win_entries = [f"Wins[{current_score}, {opponent_score}, {num_dice}] = {count}" 
                    for (current_score, opponent_score, num_dice), count in self.wins.items()]
        loss_entries = [f"Losses[{current_score}, {opponent_score}, {num_dice}] = {count}" 
                        for (current_score, opponent_score, num_dice), count in self.losses.items()]

        print_debug(Fore.MAGENTA + "Wins table: ")
        print_debug(', '.join(win_entries))
        print_debug(Fore.MAGENTA + "Losses table: ")
        print_debug(', '.join(loss_entries))

class DiceGame:
    def __init__(self, num_dice, num_sides, low_score, high_score):
        self.num_dice = num_dice
        self.num_sides = num_sides
        self.low_score = low_score
        self.high_score = high_score

    def roll_dice(self, num_dice):
        # Generate a random rolls between 1 and num_sides for each dice
        rolls = [random.randint(1, self.num_sides) for _ in range(num_dice)]
        return sum(rolls), rolls

    def play_dice_game(self, q_learning):
        player_A_score = 0
        player_B_score = 0
        player_A_history = []
        player_B_history = []
        turn = True # True for Player A, False for Player B

        # Play until some player wins or loses
        while True:
            # Choose the number of dice to roll based on the current game state
            num_dice = q_learning.choose_number_of_dice(player_A_score if turn else player_B_score, player_B_score if turn else player_A_score)
            
            # Roll the dice and get the result and the individual rolls
            roll_result, rolls = self.roll_dice(num_dice)

            print(Fore.CYAN + f"\n{'A' if turn else 'B'} rolls {num_dice} dice ({', '.join(str(roll) for roll in rolls)}) for a score of {roll_result}")

            if turn:
                # Append current state to player A's history and update player A's score
                player_A_history.append((player_A_score, player_B_score, num_dice))
                player_A_score += roll_result

                print(Fore.CYAN + f"Scores: A = {player_A_score}, B = {player_B_score}")

                # Check if player A wins or loses and update training tables accordingly
                if player_A_score > self.high_score:
                    q_learning.update_training_tables(player_B_history, player_A_history)
                    return 'Player A loses'
                elif self.low_score <= player_A_score <= self.high_score:
                    q_learning.update_training_tables(player_A_history, player_B_history)
                    return 'Player A wins'
            else:
                # Append current state to player B's history and update player Bs score
                player_B_history.append((player_B_score, player_A_score, num_dice))
                player_B_score += roll_result

                print(Fore.CYAN + f"Scores: A = {player_A_score}, B = {player_B_score}")

                # Check if player B wins or loses and update training tables accordingly
                if player_B_score > self.high_score:
                    q_learning.update_training_tables(player_A_history, player_B_history)
                    return 'Player B loses'
                elif self.low_score <= player_B_score <= self.high_score:
                    q_learning.update_training_tables(player_B_history, player_A_history)
                    return 'Player B wins'
            
            # Switch turns for next round
            turn = not turn

def print_debug(message):
    global verbose
    if verbose:
        print(message)

def parse_args():
    parser = argparse.ArgumentParser(description="Dice Game Simulation")
    parser.add_argument("-NS", type=int, required=True, help="Number of sides on each die")
    parser.add_argument("-ND", type=int, required=True, help="Maximum number of dice to choose from")
    parser.add_argument("-H", type=int, required=True, help="High winning score (inclusive)")
    parser.add_argument("-L", type=int, required=True, help="Low winning score (inclusive)")
    parser.add_argument("-G", type=int, required=True, help="Number of games to train against")
    parser.add_argument("-M", type=int, required=True, help="Exploration parameter")
    parser.add_argument("-v", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    # Perform input validation
    if args.NS <= 1 or args.ND <= 1:
        parser.error("NS and ND must be greater than 1.")
    if args.H < args.L:
        parser.error("High winning score H must be greater than or equal to low winning score L.")
    if args.G < 1:
        parser.error("Number of games G must be at least 1.")
    if args.M < 0:
        parser.error("Exploration parameter M must be non-negative.")

    return args

if __name__ == "__main__":
    args = parse_args()
    verbose = args.v

    print_debug(Fore.MAGENTA + "\nChosen settings:")
    print_debug(f"Number of sides on each die: {args.NS}")
    print_debug(f"Maximum number of dice: {args.ND}")
    print_debug(f"Low winning score: {args.L}")
    print_debug(f"High winning score: {args.H}")
    print_debug(f"Number of games: {args.G}")
    print_debug(f"Exploration parameter: {args.M}")
    print_debug(f"Verbose mode: {'Enabled' if args.v else 'Disabled'}")

    game = DiceGame(args.ND, args.NS, args.L, args.H)
    q_learning = QLearning(args.ND, args.M)

    for i in range(args.G):
        print(Fore.MAGENTA + f"\n\nPlaying game #{i+1}:")
        result = game.play_dice_game(q_learning)
        print(Fore.GREEN + f"\n{result}")
        print_debug("")
        q_learning.print_debug_training_tables()