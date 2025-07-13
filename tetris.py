import tkinter as tk
import random

# Cross-platform sound support
import sys
SOUND = True
try:
    if sys.platform.startswith('win'):
        import winsound
    else:
        import os
        import threading
        def beep(frequency, duration):
            if os.system('which play > /dev/null 2>&1') == 0:
                os.system(f'play -nq -t alsa synth {duration/1000:.2f} sine {frequency} >/dev/null 2>&1 &')
            elif os.system('which beep > /dev/null 2>&1') == 0:
                os.system(f'beep -f {frequency} -l {duration}')
        winsound = type('winsound', (), {'Beep': staticmethod(lambda f, d: threading.Thread(target=beep, args=(f, d)).start())})
except Exception:
    SOUND = False

CELL_SIZE = 30
COLS = 10
ROWS = 20
SPEED = 500  # ms

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]
COLORS = ["cyan", "yellow", "purple", "blue", "orange", "green", "red"]

class Tetris(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tetris")
        self.resizable(False, False)
        self.theme = 'dark'
        self.bg_colors = {'dark': 'black', 'light': '#f0f0f0'}
        self.fg_colors = {'dark': 'white', 'light': 'black'}
        self.canvas = tk.Canvas(self, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE, bg=self.bg_colors[self.theme])
        self.canvas.pack(side=tk.LEFT)
        # Next piece preview (smaller, closer)
        self.preview_canvas = tk.Canvas(self, width=3*CELL_SIZE, height=3*CELL_SIZE, bg=self.bg_colors[self.theme], highlightthickness=2, highlightbackground='gray')
        self.preview_canvas.place(x=COLS*CELL_SIZE-3*CELL_SIZE-10, y=10)
        # Hold piece preview
        self.hold_canvas = tk.Canvas(self, width=3*CELL_SIZE, height=3*CELL_SIZE, bg=self.bg_colors[self.theme], highlightthickness=2, highlightbackground='gray')
        self.hold_canvas.place(x=10, y=10)
        self.score = 0
        self.high_score = self._load_high_score()
        self.lines_cleared = 0
        self.level = 1
        self.soft_drop = False
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current = None
        self.current_color = None
        self.current_pos = [0, 3]
        self.next_piece = None
        self.next_color = None
        self.hold_piece = None
        self.hold_color = None
        self.hold_used = False
        self.game_over = False
        self._new_piece(init=True)
        self._draw_board()
        self._draw_preview()
        self.bind("<Key>", self._on_key)
        self.bind("<KeyRelease>", self._on_key_release)
        self.after(self._get_speed(), self._tick)
        self.score_label = tk.Label(self, text=f"Score: {self.score}", font=("Arial", 14), bg=self.bg_colors[self.theme], fg=self.fg_colors[self.theme])
        self.score_label.pack(fill=tk.X)
        self.level_label = tk.Label(self, text=f"Level: {self.level}", font=("Arial", 12), bg=self.bg_colors[self.theme], fg="#00adb5")
        self.level_label.pack(fill=tk.X)
        self.lines_label = tk.Label(self, text=f"Lines: {self.lines_cleared}", font=("Arial", 12), bg=self.bg_colors[self.theme], fg="#00adb5")
        self.lines_label.pack(fill=tk.X)
        self.high_score_label = tk.Label(self, text=f"High Score: {self.high_score}", font=("Arial", 14), bg=self.bg_colors[self.theme], fg="gold")
        self.high_score_label.pack(fill=tk.X)
        btn_frame = tk.Frame(self, bg=self.bg_colors[self.theme])
        btn_frame.pack(pady=5)
        self.restart_btn = tk.Button(btn_frame, text="⟳ Restart", font=("Arial", 12, "bold"), bg="#222", fg="white", command=self._restart, relief=tk.RAISED, width=10)
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = tk.Button(btn_frame, text="⏸ Pause", font=("Arial", 12, "bold"), bg="#444", fg="white", command=self._toggle_pause, relief=tk.RAISED, width=10)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

    def _get_speed(self):
        # Classic Tetris: speed increases with level, min 50ms
        return max(50, SPEED - (self.level-1)*40)

    def _play_sound(self, event):
        if not SOUND:
            return
        if event == 'line':
            winsound.Beep(523, 60)
        elif event == 'move':
            winsound.Beep(392, 20)
        elif event == 'rotate':
            winsound.Beep(659, 40)
        elif event == 'gameover':
            winsound.Beep(220, 300)
        elif event == 'drop':
            winsound.Beep(349, 30)

    def _load_high_score(self):
        try:
            with open("tetris_highscore.txt", "r") as f:
                return int(f.read())
        except Exception:
            return 0

    def _save_high_score(self):
        try:
            with open("tetris_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def _restart(self):
        self.score = 0
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current = None
        self.current_color = None
        self.current_pos = [0, 3]
        self.next_piece = None
        self.next_color = None
        self.hold_piece = None
        self.hold_color = None
        self.hold_used = False
        self.game_over = False
        self.score_label.config(text=f"Score: {self.score}")
        self._new_piece(init=True)
        self._draw_board()
        self._draw_preview()

    def _new_piece(self, init=False):
        # If there is no next piece, game over
        if not init and (self.next_piece is None or self.next_color is None):
            self.game_over = True
            self._draw_board()
            self._draw_preview()
            self.canvas.create_text(COLS*CELL_SIZE//2, ROWS*CELL_SIZE//2, text="GAME OVER", fill="red", font=("Arial", 24, "bold"))
            self._play_sound('gameover')
            return
        if init or self.next_piece is None:
            idx = random.randint(0, len(SHAPES)-1)
            self.current = [row[:] for row in SHAPES[idx]]
            self.current_color = COLORS[idx]
            idx2 = random.randint(0, len(SHAPES)-1)
            self.next_piece = [row[:] for row in SHAPES[idx2]] if len(SHAPES) > 0 else None
            self.next_color = COLORS[idx2] if len(COLORS) > 0 else None
        else:
            self.current = self.next_piece
            self.current_color = self.next_color
            # Simulate 'no next piece' scenario: if SHAPES is empty, set next_piece to None
            if len(SHAPES) == 0:
                self.next_piece = None
                self.next_color = None
            else:
                idx2 = random.randint(0, len(SHAPES)-1)
                self.next_piece = [row[:] for row in SHAPES[idx2]]
                self.next_color = COLORS[idx2]
        self.current_pos = [0, COLS//2 - len(self.current[0])//2]
        if self._collides(self.current, self.current_pos):
            self.game_over = True
            self._draw_board()
            self._draw_preview()
            self.canvas.create_text(COLS*CELL_SIZE//2, ROWS*CELL_SIZE//2, text="GAME OVER", fill="red", font=("Arial", 24, "bold"))
            self._play_sound('gameover')
            return
        self.hold_used = False
        self._draw_preview()

    def _draw_preview(self):
        self.preview_canvas.delete("all")
        if self.next_piece:
            rows = len(self.next_piece)
            cols = len(self.next_piece[0])
            x_offset = (3 - cols) // 2
            y_offset = (3 - rows) // 2
            for r, row in enumerate(self.next_piece):
                for c, val in enumerate(row):
                    if val:
                        x0 = (c + x_offset) * CELL_SIZE * 0.7
                        y0 = (r + y_offset) * CELL_SIZE * 0.7
                        x1 = x0 + CELL_SIZE * 0.7
                        y1 = y0 + CELL_SIZE * 0.7
                        self.preview_canvas.create_rectangle(x0, y0, x1, y1, fill=self.next_color, outline="grey")
        self.preview_canvas.create_text(1.5*CELL_SIZE, 2.7*CELL_SIZE, text="Next", fill=self.fg_colors[self.theme], font=("Arial", 9, "bold"))
        # Draw hold piece
        self.hold_canvas.delete("all")
        if self.hold_piece:
            rows = len(self.hold_piece)
            cols = len(self.hold_piece[0])
            x_offset = (3 - cols) // 2
            y_offset = (3 - rows) // 2
            for r, row in enumerate(self.hold_piece):
                for c, val in enumerate(row):
                    if val:
                        x0 = (c + x_offset) * CELL_SIZE * 0.7
                        y0 = (r + y_offset) * CELL_SIZE * 0.7
                        x1 = x0 + CELL_SIZE * 0.7
                        y1 = y0 + CELL_SIZE * 0.7
                        self.hold_canvas.create_rectangle(x0, y0, x1, y1, fill=self.hold_color, outline="grey")
        self.hold_canvas.create_text(1.5*CELL_SIZE, 2.7*CELL_SIZE, text="Hold", fill=self.fg_colors[self.theme], font=("Arial", 9, "bold"))

    def _draw_board(self):
        self.canvas.delete("all")
        # Draw ghost piece
        if not self.game_over and self.current:
            ghost_pos = list(self.current_pos)
            while not self._collides(self.current, [ghost_pos[0]+1, ghost_pos[1]]):
                ghost_pos[0] += 1
            for r, row in enumerate(self.current):
                for c, val in enumerate(row):
                    if val:
                        x0 = (ghost_pos[1]+c) * CELL_SIZE
                        y0 = (ghost_pos[0]+r) * CELL_SIZE
                        x1 = x0 + CELL_SIZE
                        y1 = y0 + CELL_SIZE
                        self.canvas.create_rectangle(x0, y0, x1, y1, fill='', outline=self.current_color, width=2, dash=(2,2))
        for r in range(ROWS):
            for c in range(COLS):
                color = self.board[r][c]
                if color:
                    self._draw_cell(r, c, color)
        if not self.game_over and self.current:
            for r, row in enumerate(self.current):
                for c, val in enumerate(row):
                    if val:
                        self._draw_cell(self.current_pos[0]+r, self.current_pos[1]+c, self.current_color)

    def _draw_cell(self, r, c, color):
        x0 = c * CELL_SIZE
        y0 = r * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="grey")

    def _collides(self, shape, pos):
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    rr = pos[0]+r
                    cc = pos[1]+c
                    if rr < 0 or rr >= ROWS or cc < 0 or cc >= COLS:
                        return True
                    if self.board[rr][cc]:
                        return True
        return False

    def _merge(self):
        for r, row in enumerate(self.current):
            for c, val in enumerate(row):
                if val:
                    self.board[self.current_pos[0]+r][self.current_pos[1]+c] = self.current_color
        # Check for game over: if any cell in the top row is filled after merging, game over
        if any(self.board[0][col] is not None for col in range(COLS)):
            self.game_over = True
            self._draw_board()
            self._draw_preview()
            self.canvas.create_text(COLS*CELL_SIZE//2, ROWS*CELL_SIZE//2, text="GAME OVER", fill="red", font=("Arial", 24, "bold"))
            self._play_sound('gameover')
            return
        self._clear_lines()
        self._new_piece()

    def _clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        lines_cleared = ROWS - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [None for _ in range(COLS)])
        self.board = new_board
        if lines_cleared > 0:
            self._play_sound('line')
            self.lines_cleared += lines_cleared
            # Level up every 10 lines
            old_level = self.level
            self.level = 1 + self.lines_cleared // 10
            if self.level != old_level:
                self.level_label.config(text=f"Level: {self.level}")
        self.score += lines_cleared * 100 * self.level
        self.score_label.config(text=f"Score: {self.score}")
        self.lines_label.config(text=f"Lines: {self.lines_cleared}")
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
            self.high_score_label.config(text=f"High Score: {self.high_score}")

    def _tick(self):
        if self.game_over:
            return
        pos = [self.current_pos[0]+1, self.current_pos[1]]
        drop_speed = self._get_speed()
        if self.soft_drop:
            drop_speed = 30  # Fast drop when down arrow held
        if not self._collides(self.current, pos):
            self.current_pos = pos
        else:
            self._merge()
        self._draw_board()
        self.after(drop_speed, self._tick)

    def _on_key(self, event):
        if self.game_over:
            return
        if event.keysym == 'Left':
            pos = [self.current_pos[0], self.current_pos[1]-1]
            if not self._collides(self.current, pos):
                self.current_pos = pos
                self._play_sound('move')
        elif event.keysym == 'Right':
            pos = [self.current_pos[0], self.current_pos[1]+1]
            if not self._collides(self.current, pos):
                self.current_pos = pos
                self._play_sound('move')
        elif event.keysym == 'Down':
            self.soft_drop = True
            pos = [self.current_pos[0]+1, self.current_pos[1]]
            if not self._collides(self.current, pos):
                self.current_pos = pos
                self._play_sound('move')
        elif event.keysym == 'Up':
            rotated = [list(row) for row in zip(*self.current[::-1])]
            if not self._collides(rotated, self.current_pos):
                self.current = rotated
                self._play_sound('rotate')
        elif event.keysym == 'space':
            # Hard drop
            while not self._collides(self.current, [self.current_pos[0]+1, self.current_pos[1]]):
                self.current_pos[0] += 1
            self._play_sound('drop')
            self._merge()
        elif event.keysym.lower() == 'c':
            # Hold piece
            if not self.hold_used:
                if self.hold_piece is None:
                    self.hold_piece = [row[:] for row in self.current]
                    self.hold_color = self.current_color
                    self._new_piece()
                else:
                    self.hold_piece, self.current = [row[:] for row in self.current], [row[:] for row in self.hold_piece]
                    self.hold_color, self.current_color = self.current_color, self.hold_color
                    self.current_pos = [0, COLS//2 - len(self.current[0])//2]
                self.hold_used = True
                self._draw_preview()
        self._draw_board()

    def _on_key_release(self, event):
        if event.keysym == 'Down':
            self.soft_drop = False

    # Pause/Resume
    def _toggle_pause(self):
        if getattr(self, '_paused', False):
            self._paused = False
            self.after(SPEED, self._tick)
            self.pause_btn.config(text="⏸ Pause", bg="#444")
        else:
            self._paused = True
            self.pause_btn.config(text="▶ Resume", bg="#0a0")

if __name__ == "__main__":
    game = Tetris()
    game.mainloop()
