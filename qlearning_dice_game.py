import argparse, random
from colorama import init, Fore

init(autoreset=True)
debug = False

def choose_number_of_dice(ND, M, current_score, opponent_score, wins, losses):
    weighted_probs = [1 / ND] * ND # Initialize to equal probability assuming no games played yet
    win_probs = []
    total_games = 0
    win_values = ""
    loss_values = ""

    print_debug(f"\nState = [{current_score}, {opponent_score}]")

    # Compute win probabilities of current state for each dice option
    for num_dice in range(1, ND + 1):
        win = wins.get((current_score, opponent_score, num_dice), 0)
        loss = losses.get((current_score, opponent_score, num_dice), 0)
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
        p_d = (total_games * w_prime_d + M) / (total_games * w_prime_d + ND * M)

        # Calculate P'd for W'd
        weighted_probs = []
        s = sum(win_probs) - w_prime_d
        for i, w_d in enumerate(win_probs):
            if i == best_d:
                weighted_probs.append(p_d)
            else:
                p_prime_d = (1 - p_d) * (w_d + M) / (s * total_games + (ND - 1) * M)
                weighted_probs.append(p_prime_d)

    print_debug(f"Win Probabilities = [{', '.join(str(round(p, 3)) for p in win_probs)}]")
    print_debug(f"Weighted probabilities = [{', '.join(str(round(p, 3)) for p in weighted_probs)}]")

    # Choose a dice number randomly based on the weighted probabilities
    dice_choice = random.choices(range(1, ND + 1), weights=weighted_probs, k=1)[0]
    return dice_choice

def roll_dice(num_sides, num_dice):
    # Generate a random rolls between 1 and num_sides for each dice
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    total = sum(rolls) 

    return total, rolls

def update_training_tables(wins, losses, winner_history, loser_history):
    # Update wins table with winner's history
    for state in winner_history:
        wins[state] = wins.get(state, 0) + 1

    # Update losses table with loser's history
    for state in loser_history:
        losses[state] = losses.get(state, 0) + 1

def play_dice_game(ND, NS, L, H, M, wins, losses):
    player_A_score = 0
    player_B_score = 0
    player_A_history = []
    player_B_history = []
    turn = True # True for Player A, False for Player B

    # Play until some player wins or loses
    while True:
        # Choose the number of dice to roll based on the current game state
        num_dice = choose_number_of_dice(ND, M, player_A_score if turn else player_B_score, 
                               player_B_score if turn else player_A_score, wins, losses)
        
        # Roll the dice and get the result and the individual rolls
        roll_result, rolls = roll_dice(NS, num_dice)

        print(Fore.CYAN + f"\n{'A' if turn else 'B'} rolls {num_dice} dice ({', '.join(str(roll) for roll in rolls)}) for a score of {roll_result}")

        if turn:
            # Append current state to player A's history and update player A's score
            player_A_history.append((player_A_score, player_B_score, num_dice))
            player_A_score += roll_result

            print(Fore.CYAN + f"Scores: A = {player_A_score}, B = {player_B_score}")

            # Check if player A wins or loses and update training tables accordingly
            if player_A_score > H:
                update_training_tables(losses, wins, player_A_history, player_B_history)
                return 'Player A loses'
            elif L <= player_A_score <= H:
                update_training_tables(wins, losses, player_A_history, player_B_history)
                return 'Player A wins'
        else:
            # Append current state to player B's history and update player Bs score
            player_B_history.append((player_B_score, player_A_score, num_dice))
            player_B_score += roll_result

            print(Fore.CYAN + f"Scores: A = {player_A_score}, B = {player_B_score}")

            # Check if player B wins or loses and update training tables accordingly
            if player_B_score > H and player_B_score >= L:
                update_training_tables(losses, wins, player_B_history, player_A_history)
                return 'Player B loses'
            elif L <= player_B_score <= H:
                update_training_tables(wins, losses, player_B_history, player_A_history)
                return 'Player B wins'
        
        # Switch turns for next round
        turn = not turn

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

def print_debug(*args, **kwargs):
    if debug:
        print(*args, **kwargs)

def print_debug_training_tables(wins, losses):
    win_entries = [f"Wins[{current_score}, {opponent_score}, {num_dice}] = {count}" 
                   for (current_score, opponent_score, num_dice), count in wins.items()]
    loss_entries = [f"Losses[{current_score}, {opponent_score}, {num_dice}] = {count}" 
                    for (current_score, opponent_score, num_dice), count in losses.items()]

    print_debug("Wins table: ")
    print_debug(', '.join(win_entries))
    print_debug("Losses table: ")
    print_debug(', '.join(loss_entries))

if __name__ == "__main__":
    args = parse_args()
    debug = args.v

    print_debug("\nChosen settings:")
    print_debug(f"Number of sides on each die: {args.NS}")
    print_debug(f"Maximum number of dice: {args.ND}")
    print_debug(f"Low winning score: {args.L}")
    print_debug(f"High winning score: {args.H}")
    print_debug(f"Number of games: {args.G}")
    print_debug(f"Exploration parameter: {args.M}")
    print_debug(f"Verbose mode: {'Enabled' if args.v else 'Disabled'}")

    wins = {}
    losses = {}

    for i in range(args.G):
        print(Fore.MAGENTA + f"\n\nPlaying game #{i+1}:")
        result = play_dice_game(args.ND, args.NS, args.L, args.H, args.M, wins, losses)
        print(Fore.GREEN + f"\n{result}")
        print_debug()
        print_debug_training_tables(wins, losses)