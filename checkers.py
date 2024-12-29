import argparse
import copy
import sys
import time

cache = {}  # FOr state caching

class State:
    def __init__(self, board):
        self.board = board
        self.width = 8
        self.height = 8

    def display(self):
        for row in self.board:
            print("".join(row))
        print()

    def __str__(self):
        return "\n".join("".join(row) for row in self.board)

    def __hash__(self):
        return hash(str(self))

def get_opp_char(player):
    return ['r', 'R'] if player in ['b', 'B'] else ['b', 'B']

def get_next_turn(curr_turn):
    return 'b' if curr_turn == 'r' else 'r'

def read_from_file(filename):
    with open(filename, 'r') as f:
        return [list(line.strip()) for line in f]

def is_valid_pos(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def get_simple_moves(state, player):
    #print("simplemovr")
    moves = []
    direction = -1 if player in ['r', 'R'] else 1  # Red moves up (-1), Black moves down (1)

    for x in range(8):
        for y in range(8):
            if state.board[x][y].lower() == player:
                # Regular piece moves: b,r
                if not state.board[x][y].isupper():
                    for dy in [-1, 1]:  # Left and right diagonal
                        new_x = x + direction
                        new_y = y + dy
                        if is_valid_pos(new_x, new_y) and state.board[new_x][new_y] == '.':
                            moves.append(((x, y), (new_x, new_y)))
                # King moves: B,R
                else:
                    for dx in [-1, 1]:  # Both directions
                        for dy in [-1, 1]:  # Left and right diagonal
                            new_x = x + dx
                            new_y = y + dy
                            if is_valid_pos(new_x, new_y) and state.board[new_x][new_y] == '.':
                                moves.append(((x, y), (new_x, new_y)))
    return moves


def get_jump_sequences(state, x, y, player, sequence=None):
    #print("getjumpseq")
    if sequence is None:
        sequence = [(x, y)]

    jumps = []
    # Define all possible directions for jumps
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    # For regular pieces, restrict anY directions based on the player
    if not state.board[x][y].isupper():  # Not a king
        if player in ['r', 'R']:
            directions = [(-1, 1), (-1, -1)]  # Red moves up
        else:
            directions = [(1, 1), (1, -1)]    # Black moves downs

    for dx, dy in directions:
        new_x, new_y = x + dx*2, y + dy*2
        if is_valid_pos(new_x, new_y) and state.board[new_x][new_y] == '.':
            mid_x, mid_y = x + dx, y + dy
            if state.board[mid_x][mid_y].lower() in get_opp_char(player):
                new_sequence = sequence + [(new_x, new_y)]
                # Only add the sequence if it ends a position we haven't visited
                if (new_x, new_y) not in sequence:
                    jumps.append(new_sequence)
                    #print(state)
                    # Recursively find multi-jumps
                    new_state = State(copy.deepcopy(state.board))
                    new_state.board[new_x][new_y] = new_state.board[x][y]
                    new_state.board[x][y] = '.'
                    new_state.board[mid_x][mid_y] = '.'
                    #print(state)
                    multi_jumps = get_jump_sequences(new_state, new_x, new_y, player, new_sequence)
                    jumps.extend(multi_jumps)

    return jumps


def get_all_jumps(state, player):
    # print("alljumps")
    all_jumps = []
    for x in range(8):
        for y in range(8):
            if state.board[x][y].lower() == player:
                # print("HERE",x,y)
                # print(state)
                all_jumps.extend(get_jump_sequences(state, x, y, player))

    return all_jumps

def generate_successors(state, player):
    # Generate all ofde possible jumps
    #print("gensuccessr")
    jumps = get_all_jumps(state, player)

    if jumps:
        # If there are jumps, generate successors for the entire jump sequence
        successor_states = []
        for jump_sequence in jumps:
            new_state = State(copy.deepcopy(state.board))
            for i in range(len(jump_sequence) - 1):
                start = jump_sequence[i]
                end = jump_sequence[i + 1]
                new_state = apply_move(new_state, start, end)
            successor_states.append(new_state)
        return successor_states
    else:
        # If no jumps are available, generate simple moves
        return [apply_move(state, move[0], move[1]) for move in get_simple_moves(state, player)]

def apply_move(state, start, end):
    #print("applymovr")
    new_state = State(copy.deepcopy(state.board))
    x1, y1 = start
    x2, y2 = end
    new_state.board[x2][y2] = new_state.board[x1][y1]
    new_state.board[x1][y1] = '.'

    # Handle jumps: clear the middle piece
    if abs(x2 - x1) == 2:
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        new_state.board[mid_x][mid_y] = '.'

    # Handle king promotion
    if new_state.board[x2][y2] == 'r' and x2 == 0:
        new_state.board[x2][y2] = 'R'
    elif new_state.board[x2][y2] == 'b' and x2 == 7:
        new_state.board[x2][y2] = 'B'
    # print(state)
    return new_state


def utility(state, player, depth):
    #print("utilityr")
    opp = 'b' if player == 'r' else 'r'

    # Count pieces
    player_pieces = sum(row.count(player) for row in state.board)
    player_kings = sum(row.count(player.upper()) for row in state.board)
    opp_pieces = sum(row.count(opp) for row in state.board)
    opp_kings = sum(row.count(opp.upper()) for row in state.board)

    total_player = player_pieces + player_kings
    total_opp = opp_pieces + opp_kings

    # Terminal state checks with depth consideration
    if total_opp == 0 or (not generate_successors(state, opp)):
        return 1000000 - depth  # Win sooner is better
    elif total_player == 0 or (not generate_successors(state, player)):
        return -1000000 + depth  # Lose later is better

    # Non-terminal evaluation
    player_value = player_pieces + 2 * player_kings
    opp_value = opp_pieces + 2 * opp_kings
    # print(state)
    # Return the difference in value
    return player_value - opp_value

def evaluate(state, player):
    # print("evalfn")
    opp = 'b' if player == 'r' else 'r'

    # Count the number of pieces for both players
    player_pieces = sum(row.count(player) for row in state.board)
    player_kings = sum(row.count(player.upper()) for row in state.board)
    opp_pieces = sum(row.count(opp) for row in state.board)
    opp_kings = sum(row.count(opp.upper()) for row in state.board)

    # Add more value for controlling the center (squares like [3, 3], [4, 4])
    center_positions = [(3, 3), (3, 4), (4, 3), (4, 4)]
    # Center is pretty much better
    center_value = 0
    for x, y in center_positions:
        if state.board[x][y].lower() == player:
            center_value += 1
        # Try and prolong the length of opponent player loss
        elif state.board[x][y].lower() == opp:
            center_value -= 1

    # Give more weight to kings and add additional value for controlling the center
    player_value = player_pieces + 2.5 * player_kings + center_value
    opp_value = opp_pieces + 2.5 * opp_kings - center_value

    return player_value - opp_value


cache = {}
def alpha_beta(state, depth, alpha, beta, maximizing_player, player):
    """
    Alpha-beta pruning with depth-limited search.
    Looks at the entire tree until the specified depth and prunes unnecessary branches.
    """
    #print("absearch")
    state_hash = hash(state)

    if state_hash in cache and cache[state_hash]['depth'] >= depth:
        return cache[state_hash]['value']

    # Check for terminal state
    terminal_value = utility(state, player, depth)
    if depth == 0 or abs(terminal_value) > 999999:  # Terminal state check
        cache[state_hash] = {'depth': depth, 'value': terminal_value}
        return terminal_value

    successors = generate_successors(state, player if maximizing_player else get_opp_char(player)[0])

    if not successors:
        value = utility(state, player, depth)
        cache[state_hash] = {'depth': depth, 'value': value}
        return value

    # Sort moves based on preliminary evaluation
    if maximizing_player:
        successors.sort(key=lambda s: evaluate(s, player), reverse=True)
    else:
        successors.sort(key=lambda s: evaluate(s, get_opp_char(player)[0]), reverse=True)
    # print(state)
    if maximizing_player:
        value = float('-inf')
        for successor in successors:
            value = max(value, alpha_beta(successor, depth - 1, alpha, beta, False, player))
            alpha = max(alpha, value)
            if beta <= alpha:
                break
    else:
        value = float('inf')
        for successor in successors:
            value = min(value, alpha_beta(successor, depth - 1, alpha, beta, True, player))
            beta = min(beta, value)
            if beta <= alpha:
                break
    # print(state)
    cache[state_hash] = {'depth': depth, 'value': value}
    return value


def get_best_move(state, player, depth):
    """
    Determines the best move using alpha-beta pruning and evaluates the game tree
    up to the specified depth.
    """
    best_value = float('-inf') if player == 'r' else float('inf')
    best_move = None
    alpha = float('-inf')
    beta = float('inf')

    successors = generate_successors(state, player)
    if not successors:
        return None

    # Sort moves for initial ordering
    if player == 'r':
        successors.sort(key=lambda s: evaluate(s, player), reverse=True)
    else:
        successors.sort(key=lambda s: evaluate(s, player))

    for successor in successors:
        value = alpha_beta(successor, depth - 1, alpha, beta, player != 'r', player)

        # If maximizing player ie player red
        if player == 'r':
            if value >= best_value:
                best_value = value
                best_move = successor
            alpha = max(alpha, value)

        # If minimizing player ie player black
        else:
            if value <= best_value:
                best_value = value
                best_move = successor
            beta = min(beta, value)

    return best_move



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()

    # To use while running the code
    # inputf = str(input("Please Enter Input file name: "))
    # inputf = inputf + ".txt"
    # # inputf = "checkers1.txt"
    # outputf = inputf[:-4] + "_sol.txt"
    initial_board = read_from_file(args.inputfile)
    # initial_board = read_from_file(inputf)

    state = State(initial_board)
    turn = 'r'
    depth = 11  # You can adjust this value

    # Code for debugging
    # c = 0
    # while True:
    #     print("PRINTRhere")
    #     state.display()
    #     best_move = get_best_move(state, turn, depth)
    #     print("PRINTRhere2")
    #     print(best_move)
    #     c += 1
    #     if best_move is None or c >= 3:
    #         break
    #
    #
    #     state = best_move
    #     turn = get_next_turn(turn)

    with open(args.outputfile, 'w') as f:
    # with open(outputf, 'w') as f:
        sys.stdout = f

        while True:
            state.display()
            best_move = get_best_move(state, turn, depth)
            # print(best_move)
            if best_move is None:
                break

            state = best_move
            turn = get_next_turn(turn)

        sys.stdout = sys.__stdout__
