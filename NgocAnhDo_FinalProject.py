"""
2048: Hogwarts House Edition
"""
import random
import tkinter as tk

BOARD_SIZE = 4
CELL_PX = 90
GAP_PX = 10
MARGIN_PX = 14

PARCHMENT = "#f1e3c6"
BOARD_BG = "#5c4420"
HEADER_BG = "#2b1d12"
MAROON = "#740001"
GOLD = "#d4af37"
INK = "#241a0f"

def rounded_rect(canvas, x0, y0, x1, y1, radius, **kwargs):
    points = [
        x0 + radius, y0,
        x1 - radius, y0,
        x1, y0,
        x1, y0 + radius,
        x1, y1 - radius,
        x1, y1,
        x1 - radius, y1,
        x0 + radius, y1,
        x0, y1,
        x0, y1 - radius,
        x0, y0 + radius,
        x0, y0,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

# ---------------------------------------------------------------------
# Tile data
# ---------------------------------------------------------------------

TILES = {
    2:    {"name": "Harry Potter",     "short": "Harry",      "bg": "#8b1d2e", "icon": "⚡"},
    4:    {"name": "Ron Weasley",      "short": "Ron",        "bg": "#b05e26", "icon": "♞"},
    8:    {"name": "Hermione Granger", "short": "Hermione",   "bg": "#784614", "icon": "📚"},
    16:   {"name": "Draco Malfoy",     "short": "Draco",      "bg": "#32383c", "icon": "🐉"},
    32:   {"name": "Severus Snape",    "short": "Snape",      "bg": "#1c1c1e", "icon": "🧪"},
    64:   {"name": "Gryffindor",       "short": "Gryff",      "bg": "#8b1d2e", "icon": "🦁"},
    128:  {"name": "Slytherin",        "short": "Slyth",      "bg": "#124a3a", "icon": "🐍"},
    256:  {"name": "Hufflepuff",       "short": "Huffl",      "bg": "#e0a02c", "icon": "🦡"},
    512:  {"name": "Ravenclaw",        "short": "Raven",      "bg": "#1a2a4a", "icon": "🦅"},
    1024: {"name": "Albus Dumbledore", "short": "Dumbledore", "bg": "#3c285f", "icon": "👓"},
    2048: {"name": "Lord Voldemort",   "short": "Voldemort",  "bg": "#0a0a0a", "icon": "💀"},
}
WIN_VALUE = max(TILES)
FALLBACK_BG = "#2e144a"
EMPTY_BG = "#caa472"


def text_color_for(hex_bg):
    hex_bg = hex_bg.lstrip("#")
    r, g, b = int(hex_bg[0:2], 16), int(hex_bg[2:4], 16), int(hex_bg[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#1a1a1a" if brightness > 170 else "#f3ead4"


# ---------------------------------------------------------------------
# Core 2048 game logic 
# ---------------------------------------------------------------------

def make_empty_board():
    return [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def empty_cells(board):
    cells = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 0:
                cells.append((row, col))
    return cells


def add_random_tile(board):
    cells = empty_cells(board)
    if not cells:
        return
    row, col = random.choice(cells)
    board[row][col] = 2 if random.random() < 0.9 else 4


def compress_and_merge(line):
    values = [v for v in line if v != 0]
    merged = []
    points = 0
    i = 0
    while i < len(values):
        if i + 1 < len(values) and values[i] == values[i + 1] and values[i] < WIN_VALUE:
            new_value = values[i] * 2
            merged.append(new_value)
            points += new_value
            i += 2
        else:
            merged.append(values[i])
            i += 1
    while len(merged) < BOARD_SIZE:
        merged.append(0)
    return merged, points


def get_row(board, row):
    return board[row][:]


def get_col(board, col):
    return [board[row][col] for row in range(BOARD_SIZE)]


def set_row(board, row, values):
    for col in range(BOARD_SIZE):
        board[row][col] = values[col]


def set_col(board, col, values):
    for row in range(BOARD_SIZE):
        board[row][col] = values[row]


def move_left(board):
    total = 0
    for row in range(BOARD_SIZE):
        new_line, points = compress_and_merge(get_row(board, row))
        set_row(board, row, new_line)
        total += points
    return total


def move_right(board):
    total = 0
    for row in range(BOARD_SIZE):
        line = get_row(board, row)[::-1]
        new_line, points = compress_and_merge(line)
        set_row(board, row, new_line[::-1])
        total += points
    return total


def move_up(board):
    total = 0
    for col in range(BOARD_SIZE):
        new_line, points = compress_and_merge(get_col(board, col))
        set_col(board, col, new_line)
        total += points
    return total


def move_down(board):
    total = 0
    for col in range(BOARD_SIZE):
        line = get_col(board, col)[::-1]
        new_line, points = compress_and_merge(line)
        set_col(board, col, new_line[::-1])
        total += points
    return total


def copy_board(board):
    return [row[:] for row in board]


def boards_equal(a, b):
    return a == b


def can_move(board):
    if empty_cells(board):
        return True
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            value = board[row][col]
            if col + 1 < BOARD_SIZE and board[row][col + 1] == value:
                return True
            if row + 1 < BOARD_SIZE and board[row + 1][col] == value:
                return True
    return False


def has_won(board):
    for row in board:
        for value in row:
            if value >= WIN_VALUE:
                return True
    return False


board = make_empty_board()
score = 0
game_over = False
won_already_announced = False

board_px = MARGIN_PX * 2 + BOARD_SIZE * CELL_PX + (BOARD_SIZE - 1) * GAP_PX

root = tk.Tk()
root.title("2048: Hogwarts House Edition")
root.configure(bg=HEADER_BG)

header = tk.Frame(root, bg=HEADER_BG, highlightbackground=GOLD, highlightthickness=2)
header.pack(fill="x", padx=18, pady=(18, 0), ipady=10)

title_label = tk.Label(header, text="2048: HOGWARTS HOUSE EDITION",
                        font=("Georgia", 20, "bold"), fg=GOLD, bg=HEADER_BG)
title_label.pack()

score_var = tk.StringVar(value="Score: 0")
score_label = tk.Label(header, textvariable=score_var, font=("Georgia", 14),
                        fg=PARCHMENT, bg=HEADER_BG)
score_label.pack(pady=(6, 0))

status_var = tk.StringVar(value="Use the arrow keys to play.")
status_label = tk.Label(root, textvariable=status_var, font=("Georgia", 11, "italic"),
                         fg="#caa", bg=HEADER_BG)
status_label.pack(pady=(10, 8))

board_frame = tk.Frame(root, bg=BOARD_BG, highlightbackground=GOLD, highlightthickness=3)
board_frame.pack(padx=18, pady=(0, 14))

canvas = tk.Canvas(board_frame, width=board_px, height=board_px, bg=BOARD_BG, highlightthickness=0)
canvas.pack(padx=8, pady=8)


def new_game():
    global board, score, game_over, won_already_announced
    board = make_empty_board()
    score = 0
    game_over = False
    won_already_announced = False
    add_random_tile(board)
    add_random_tile(board)
    status_var.set("Use the arrow keys to play.")
    draw_board()


new_game_btn = tk.Button(root, text="New Game", command=new_game,
                          font=("Georgia", 12, "bold"), bg=MAROON, fg=GOLD,
                          activebackground="#8d0003", activeforeground=GOLD,
                          relief="flat", padx=16, pady=8, cursor="hand2")
new_game_btn.pack(pady=(0, 18))


def cell_bounds(row, col):
    x0 = MARGIN_PX + col * (CELL_PX + GAP_PX)
    y0 = MARGIN_PX + row * (CELL_PX + GAP_PX)
    return x0, y0, x0 + CELL_PX, y0 + CELL_PX


def draw_board():
    canvas.delete("all")
    radius = 14
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x0, y0, x1, y1 = cell_bounds(row, col)
            value = board[row][col]

            if value == 0:
                rounded_rect(canvas, x0, y0, x1, y1, radius, fill=EMPTY_BG, outline="")
                continue

            tile = TILES.get(value)
            bg = tile["bg"] if tile else FALLBACK_BG
            fg = text_color_for(bg)

            # soft drop shadow, then the tile itself on top
            rounded_rect(canvas, x0 + 3, y0 + 4, x1 + 3, y1 + 4, radius, fill="#1a1208", outline="")
            rounded_rect(canvas, x0, y0, x1, y1, radius, fill=bg, outline="")

            if tile:
                canvas.create_text((x0 + x1) / 2, y0 + CELL_PX * 0.38,
                                    text=tile["icon"], font=("Segoe UI Emoji", 30))
                label = tile["short"]
            else:
                label = ""
            canvas.create_text((x0 + x1) / 2, y0 + CELL_PX * 0.76,
                                text=label, fill=fg, font=("Georgia", 12, "bold"))
            canvas.create_text((x0 + x1) / 2, y1 - CELL_PX * 0.10,
                                text=str(value), fill=fg, font=("Georgia", 11, "bold"))
    score_var.set(f"Score: {score}")


def handle_move(direction):
    global score, game_over, won_already_announced
    if game_over:
        return
    before = copy_board(board)
    mover = {"Up": move_up, "Down": move_down, "Left": move_left, "Right": move_right}[direction]
    points = mover(board)
    if not boards_equal(before, board):
        score += points
        add_random_tile(board)
        draw_board()
        if not won_already_announced and has_won(board):
            won_already_announced = True
            status_var.set("Voldemort has returned! You win -- keep playing for a higher score.")
        elif not can_move(board):
            game_over = True
            status_var.set(f"No more moves. Final score: {score}")


root.bind("<Up>", lambda e: handle_move("Up"))
root.bind("<Down>", lambda e: handle_move("Down"))
root.bind("<Left>", lambda e: handle_move("Left"))
root.bind("<Right>", lambda e: handle_move("Right"))

root.bind("<w>", lambda e: handle_move("Up"))
root.bind("<s>", lambda e: handle_move("Down"))
root.bind("<a>", lambda e: handle_move("Left"))
root.bind("<d>", lambda e: handle_move("Right"))


if __name__ == "__main__":
    new_game()
    root.mainloop()