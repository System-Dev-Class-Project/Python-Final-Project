import tkinter as tk
from tkinter import messagebox
import random
import Game_Logic
class SudokuGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sudoku")
        self.cells = {}
        self.selected = None
        self.original_cells = set()
        self.moves_history = []

        # Create menu frame
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(expand=True, fill='both')
        self.create_menu()

        # Create main game frame (initially hidden)
        self.game_frame = tk.Frame(self.root)
        self.difficulty = None
        self.solution = None

    def create_menu(self):
        title = tk.Label(self.menu_frame, text="SUDOKU", font=('Arial', 24, 'bold'))
        title.pack(pady=20)

        # Difficulty buttons
        tk.Button(self.menu_frame, text="Easy", font=('Arial', 14),
                  command=lambda: self.start_game("easy")).pack(pady=10)
        tk.Button(self.menu_frame, text="Medium", font=('Arial', 14),
                  command=lambda: self.start_game("medium")).pack(pady=10)
        tk.Button(self.menu_frame, text="Hard", font=('Arial', 14),
                  command=lambda: self.start_game("hard")).pack(pady=10)

        # Exit button
        tk.Button(self.menu_frame, text="Exit", font=('Arial', 14),
                  command=self.root.quit).pack(pady=20)

    def navigate(self, direction):
        if not self.selected:
            return

        row, col = self.selected

        # Define movement logic and skip original cells
        while True:
            if direction == "Up" and row > 0:
                row -= 1
            elif direction == "Down" and row < 8:
                row += 1
            elif direction == "Left" and col > 0:
                col -= 1
            elif direction == "Right" and col < 8:
                col += 1
            else:
                break  # Stop if we're at the edge of the grid

            # If the new cell is not prefilled, select it and exit
            if (row, col) not in self.original_cells:
                self.selected = (row, col)
                self.cells[self.selected].focus_set()
                break



    def create_game_ui(self):
        # Destroy existing game frame if it exists
        if hasattr(self, 'grid_frame'):
            self.grid_frame.destroy()

        # Clear menu frame
        self.menu_frame.pack_forget()

        # Setup game frame
        self.game_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Create grid
        self.grid_frame = tk.Frame(self.game_frame, bg='black')
        self.grid_frame.pack(side=tk.LEFT, padx=(0, 20))

        # Create cells
        self.cells = {}  # Clear existing cells dictionary
        for i in range(9):
            for j in range(9):
                cell = tk.Entry(self.grid_frame, width=2, font=('Arial', 18),
                                justify='center')
                cell.grid(row=i, column=j, padx=1, pady=1, ipady=5)
                cell.bind('<FocusIn>', lambda e, row=i, col=j: self.cell_selected(row, col))
                cell.bind('<Key>', self.key_pressed)
                self.cells[(i, j)] = cell

                # Add thicker borders for 3x3 boxes
                if i % 3 == 0 and i != 0:
                    cell.grid(pady=(3, 1))
                if j % 3 == 0 and j != 0:
                    cell.grid(padx=(3, 1))

        # Create control panel
        control_frame = tk.Frame(self.game_frame)
        control_frame.pack(side=tk.LEFT, fill='y')

        # Undo button
        tk.Button(control_frame, text="Undo", font=('Arial', 12),
                  command=self.undo_move).pack(pady=5)

        # New Game button
        tk.Button(control_frame, text="New Game", font=('Arial', 12),
                  command=self.return_to_menu).pack(pady=5)

        # Exit button
        tk.Button(control_frame, text="Exit", font=('Arial', 12),
                  command=self.root.quit).pack(pady=5)

        # Timer label
        self.timer_label = tk.Label(control_frame, text="Time: 00:00", font=('Arial', 12))
        self.timer_label.pack(pady=10)

        # Bind arrow keys for navigation
        self.root.bind('<Up>', lambda e: self.navigate("Up"))
        self.root.bind('<Down>', lambda e: self.navigate("Down"))
        self.root.bind('<Left>', lambda e: self.navigate("Left"))
        self.root.bind('<Right>', lambda e: self.navigate("Right"))


    def start_timer(self):
        self.seconds_elapsed = 0
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            minutes, seconds = divmod(self.seconds_elapsed, 60)
            self.timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
            self.seconds_elapsed += 1
            self.root.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def return_to_menu(self):
        # Clear game state
        self.moves_history = []
        self.original_cells = set()
        self.selected = None

        # Hide game frame and show menu
        self.game_frame.pack_forget()
        if hasattr(self, 'grid_frame'):
            self.grid_frame.destroy()
        self.menu_frame.pack(expand=True, fill='both')

    def check_win(self):
        # Check if all cells are filled correctly
        for i in range(9):
            for j in range(9):
                value = self.cells[(i, j)].get()
                if not value or not Game_Logic.is_valid_solution(i, j, int(value), self.cells):
                    return False
        return True


    def is_valid_move(self, row, col, num):
        # Check row
        for j in range(9):
            if self.cells[(row, j)].get() == str(num):
                return False

        # Check column
        for i in range(9):
            if self.cells[(i, col)].get() == str(num):
                return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.cells[(i, j)].get() == str(num):
                    return False

        return True
    def cell_selected(self, row, col):
        self.selected = (row, col)

    def key_pressed(self, event):
        if not self.selected:
            return "break"

        row, col = self.selected

        # Check if it's an original cell
        if (row, col) in self.original_cells:
            return "break"

        # Handle backspace/delete key
        if event.keysym in ('BackSpace', 'Delete'):
            # Store move in history
            old_value = self.cells[self.selected].get()
            if old_value:  # Only store if there was a value
                self.moves_history.append((row, col, old_value))

            # Clear the cell and reset its color
            self.cells[self.selected].delete(0, tk.END)
            self.cells[self.selected].config(fg='blue', bg='white')
            return "break"

        # Handle number keys
        if event.char in '123456789':
            if self.is_valid_move(row, col, int(event.char)):
                # Store move in history
                old_value = self.cells[self.selected].get()
                self.moves_history.append((row, col, old_value))

                # Update cell
                self.cells[self.selected].delete(0, tk.END)
                self.cells[self.selected].insert(0, event.char)
                self.cells[self.selected].config(fg='blue', bg='white')

                # Check if game is won
                if self.check_win():
                    self.stop_timer()
                    minutes, seconds = divmod(self.seconds_elapsed, 60)
                    time_message = f"You solved the Sudoku! Your time is {minutes} minutes and {seconds} seconds."
                    messagebox.showinfo("Congratulations!", time_message)
                    self.return_to_menu()
            else:
                # Mark invalid move with red background
                self.cells[self.selected].delete(0, tk.END)
                self.cells[self.selected].insert(0, event.char)
                self.cells[self.selected].config(bg='pink')

        return "break"  # Prevent default behavior

    def undo_move(self):
        if self.moves_history:
            row, col, value = self.moves_history.pop()
            self.cells[(row, col)].delete(0, tk.END)
            self.cells[(row, col)].config(fg='blue', bg='white')
            if value:
                self.cells[(row, col)].insert(0, value)


    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.create_game_ui()

        # Start the timer
        self.start_timer()

        # Clear game state
        self.moves_history = []
        self.original_cells = set()
        self.selected = None

        # Generate new puzzle
        puzzle, self.solution = Game_Logic.generate_puzzle(difficulty)

        # Fill the grid
        for i in range(9):
            for j in range(9):
                self.cells[(i, j)].delete(0, tk.END)
                if puzzle[i][j] != 0:
                    self.cells[(i, j)].insert(0, str(puzzle[i][j]))
                    self.cells[(i, j)].config(fg='black')
                    self.original_cells.add((i, j))
                else:
                    self.cells[(i, j)].config(fg='blue')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = SudokuGUI()
    game.run()
