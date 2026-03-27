from random import randint

COLOURS = {
    'reset': '\033[m',

    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',

    'black_bold': '\033[1;30m',
    'red_bold': '\033[1;31m',
    'green_bold': '\033[1;32m',
    'yellow_bold': '\033[1;33m',
    'blue_bold': '\033[1;34m',
    'magenta_bold': '\033[1;35m',
    'cyan_bold': '\033[1;36m',
    'white_bold': '\033[1;37m'
}

GAME_TITLE = """
██████╗  ██████╗ ██████╗      ██████╗ ██╗   ██╗████████╗██╗
██╔══██╗██╔═══██╗██╔══██╗    ██╔═══██╗██║   ██║╚══██╔══╝██║
██████╔╝██║   ██║██████╔╝    ██║   ██║██║   ██║   ██║   ██║
██╔═══╝ ██║   ██║██╔═══╝     ██║   ██║██║   ██║   ██║   ╚═╝
██║     ╚██████╔╝██║         ╚██████╔╝╚██████╔╝   ██║   ██╗
╚═╝      ╚═════╝ ╚═╝          ╚═════╝  ╚═════╝    ╚═╝   ╚═╝
                                                           """

ROWS = 6
COLS = 7
EMPTY_DOT = f"{COLOURS['white']}●{COLOURS['reset']}"
RED_DOT = f"{COLOURS['red']}●{COLOURS['reset']}"
BLUE_DOT = f"{COLOURS['blue']}●{COLOURS['reset']}"
EMPTY = 0
RED_PLAYER = 1
BLUE_PLAYER = -1
SYMBOLS = {
    EMPTY: EMPTY_DOT,
    RED_PLAYER: RED_DOT,
    BLUE_PLAYER: BLUE_DOT
}

board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
turn = 0
while turn == 0:
    turn = randint(-1, 1)

def print_title():
    print(f"{COLOURS['blue']}{GAME_TITLE}{COLOURS['reset']}")

def print_board(show_arrows = True):
    green_arrow = f" {COLOURS['green']}↓{COLOURS['reset']}"

    if show_arrows:
        print("".join((green_arrow if cell == EMPTY else "  ") for cell in board[0]))
    for row in board:
        print(f"|{"|".join(SYMBOLS[cell] for cell in row)}|")
    if show_arrows:
        print("".join((green_arrow if cell == turn else "  ") for cell in board[-1]))

def print_turn():
    if turn == RED_PLAYER:
        print(f"{COLOURS['red']}RED's turn!{COLOURS['reset']}")
    else:
        print(f"{COLOURS['blue']}BLUE's turn!{COLOURS['reset']}")

def get_player_input():
    while True:
        player_in = str(input()).split(" ")
        if len(player_in) < 2:
            print("Invalid. Type the column index (starts in 1), space, drop(d) or pop(p)")
            continue
        elif len(player_in) > 2:
            player_in = [player_in[0], player_in[1]]
        try:
            player_in = [int(player_in[0]), player_in[1][0].lower()]
        except ValueError:
            print("Invalid. Type the column index (starts in 1), space, drop(d) or pop(p)")
            continue
        if player_in[0] > COLS or player_in[0] < 0 or player_in[1] not in ["d", "p"]:
            print("Invalid. Type the column index (starts in 1), space, drop(d) or pop(p)")
            continue
        return player_in

def is_valid(move):
    if move[1] == "d" and board[0][move[0] - 1] != EMPTY:
        return False
    if move[1] == "p" and board[-1][move[0] - 1] != turn:
        return False
    return True

def make_move(move):
    if move[1] == "d":
        for i in range(ROWS - 1, -1, -1):
            if board[i][move[0] - 1] == EMPTY:
                board[i][move[0] - 1] = turn
                return
    for i in range(ROWS - 1, 0, -1):
        board[i][move[0] - 1] = board[i - 1][move[0] - 1]
    board[0][move[0] - 1] = EMPTY

def check_winner():
    wins = set()

    # horizontal win
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r][c + 1] == board[r][c + 2] == board[r][c + 3]:
                wins.add(board[r][c])

    # vertical win
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] != EMPTY and board[r][c] == board[r + 1][c] == board[r + 2][c] == board[r + 3][c]:
                wins.add(board[r][c])

    # diagonal win \
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r + 1][c + 1] == board[r + 2][c + 2] == board[r + 3][c + 3]:
                wins.add(board[r][c])

    # diagonal win /
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if board[r][c] != EMPTY and board[r][c] == board[r + 1][c - 1] == board[r + 2][c - 2] == board[r + 3][c - 3]:
                wins.add(board[r][c])

    if len(wins) == 0:
        return 0
    if len(wins) == 2:
        return turn
    return wins.pop()

def print_winner(w):
    if w == BLUE_PLAYER:
        print(f"{COLOURS['blue']}BLUE WINS!{COLOURS['reset']}")
    else:
        print(f"{COLOURS['red']}RED WINS!{COLOURS['reset']}")

def check_full_board():
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == EMPTY:
                return False
    return True

def get_ans():
    a = ""
    while a not in ["y", "n"]:
        a = str(input("yes[y] or no[n]: "))[0].lower()
    return a

# print_title()
while True:
    print_turn()
    print_board()
    if check_full_board(): # TODO
        print("The board is full. Do you want to end the game as a draw?")
        ans = get_ans()
    print("Type your move: [column] [drop/pop]")
    player_input = get_player_input()
    while not is_valid(player_input):
        print("Invalid move. Try again:")
        player_input = get_player_input()
        if check_full_board():
            print("erro") # TODO
    make_move(player_input)
    winner = check_winner()
    if winner != 0:
        print_board(show_arrows = False)
        print_winner(winner)
        break
    turn *= -1
