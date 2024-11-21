import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import Game_Logic
import time
import os
class LeaderboardManager:
    def __init__(self, db_path='leaderboard.sqlite'):
        self.db_path = db_path
        self.initialize_database()
        
        # Check if leaderboard is empty and populate if needed
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM leaderboard')
            if cursor.fetchone()[0] == 0:
                self.populate_initial_leaderboard()
    def initialize_database(self):
        """Create leaderboard database and table if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    time REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_score(self, username, difficulty, game_time):
        """Add a new score to the leaderboard."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO leaderboard (username, difficulty, time) 
                VALUES (?, ?, ?)
            ''', (username, difficulty, game_time))
            conn.commit()

    def get_top_scores(self, limit=10):
        """Retrieve top scores sorted by time."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, difficulty, time 
                FROM leaderboard 
                ORDER BY time ASC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    def populate_initial_leaderboard(self):
        """Add some initial sample scores to the leaderboard."""
        sample_scores = [
            ('Alice', 'easy', 120.5),
            ('Bob', 'medium', 180.7),
            ('Charlie', 'hard', 250.3),
            ('David', 'easy', 95.2),
            ('Eve', 'medium', 165.4),
            ('Frank', 'hard', 210.6),
            ('Grace', 'easy', 110.8),
            ('Henry', 'medium', 195.2),
            ('Isabelle', 'hard', 275.9),
            ('Jack', 'easy', 88.6)
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for username, difficulty, game_time in sample_scores:
                cursor.execute('''
                    INSERT INTO leaderboard (username, difficulty, time) 
                    VALUES (?, ?, ?)
                ''', (username, difficulty, game_time))
            conn.commit()

class UserManager:
    def __init__(self, db_path='users.sqlite'):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Create users database and table if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            # Add a default admin user if no users exist
            cursor.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                               ('admin', 'password'))
            conn.commit()

    def validate_login(self, username, password):
        """Validate user credentials."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                           (username, password))
            return cursor.fetchone() is not None

    def register_user(self, username, password):
        """Register a new user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                               (username, password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

class SudokuGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sudoku")
        self.cells = {}
        self.selected = None
        self.original_cells = set()
        self.moves_history = []

        #db greier
        self.user_manager = UserManager()
        self.leaderboard_manager = LeaderboardManager()
        # Create menu frame
        self.menu_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.menu_frame.pack(expand=True, fill='both', padx=100, pady=50)
        self.create_menu()

        # Create main game frame (initially hidden)
        self.game_frame = tk.Frame(self.root)
        self.difficulty = None
        self.solution = None

    def create_menu(self):
        title = tk.Label(self.menu_frame, text="SUDOKU", font=('Arial', 36, 'bold'))
        title.pack(pady=40)

        tk.Button(self.menu_frame, text="Easy", font=('Arial', 18), command=lambda: self.start_game("easy")).pack(pady=15, fill='x')
        tk.Button(self.menu_frame, text="Medium", font=('Arial', 18), command=lambda: self.start_game("medium")).pack(pady=15, fill='x')
        tk.Button(self.menu_frame, text="Hard", font=('Arial', 18), command=lambda: self.start_game("hard")).pack(pady=15, fill='x')

        # log in / leaderboard
        tk.Button(self.menu_frame, text="Leaderboard", font=('Arial', 18),
                  command=self.show_leaderboard).pack(pady=10)
        tk.Button(self.menu_frame, text="Guest", font=('Arial', 18),
                  command=self.start_as_guest).pack(pady=10)
        tk.Button(self.menu_frame, text="Log in", font=('Arial', 18),
                  command=self.open_login_popup).pack(pady=10)
        tk.Button(self.menu_frame, text="Register", font=('Arial', 18),
                  command=self.open_register_popup).pack(pady=10)
        # Exit button
        tk.Button(self.menu_frame, text="Exit", font=('Arial', 18, 'bold'), command=self.root.quit, fg='black').pack(pady=30)
#log in and registration

    def start_as_guest(self):
        self.current_user = "Guest"
        self.show_difficulty_selection()

    def open_login_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Login")
        popup.geometry("300x200")

        tk.Label(popup, text="Username:").pack(pady=5)
        username_entry = tk.Entry(popup)
        username_entry.pack()

        tk.Label(popup, text="Password:").pack(pady=5)
        password_entry = tk.Entry(popup, show="*")
        password_entry.pack()

        def handle_login():
            username = username_entry.get()
            password = password_entry.get()

            if self.user_manager.validate_login(username, password):
                self.current_user = username
                messagebox.showinfo("Login", f"Welcome, {username}!")
                popup.destroy()
                self.show_difficulty_selection()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials")

        tk.Button(popup, text="Login", command=handle_login).pack(pady=10)

    def open_register_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Register")
        popup.geometry("300x250")

        tk.Label(popup, text="Username:").pack(pady=5)
        username_entry = tk.Entry(popup)
        username_entry.pack()

        tk.Label(popup, text="Password:").pack(pady=5)
        password_entry = tk.Entry(popup, show="*")
        password_entry.pack()

        tk.Label(popup, text="Confirm Password:").pack(pady=5)
        confirm_entry = tk.Entry(popup, show="*")
        confirm_entry.pack()

        def handle_registration():
            username = username_entry.get()
            password = password_entry.get()
            confirm = confirm_entry.get()

            if not username or not password:
                messagebox.showerror("Error", "All fields are required")
                return

            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return

            if self.user_manager.register_user(username, password):
                messagebox.showinfo("Success", "Registration successful!")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Username already exists")

        tk.Button(popup, text="Register", command=handle_registration).pack(pady=10)

#leaderboard
    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Leaderboard")
        leaderboard_window.geometry("400x400")

        scores = self.leaderboard_manager.get_top_scores()

        tk.Label(leaderboard_window, text="Top Scores", font=('Arial', 18)).pack(pady=10)

        leaderboard_frame = tk.Frame(leaderboard_window)
        leaderboard_frame.pack(expand=True, fill='both', padx=20)

        tk.Label(leaderboard_frame, text="Rank", font=('Arial', 12)).grid(row=0, column=0)
        tk.Label(leaderboard_frame, text="Username", font=('Arial', 12)).grid(row=0, column=1)
        tk.Label(leaderboard_frame, text="Difficulty", font=('Arial', 12)).grid(row=0, column=2)
        tk.Label(leaderboard_frame, text="Time", font=('Arial', 12)).grid(row=0, column=3)

        for rank, (username, difficulty, time) in enumerate(scores, 1):
            tk.Label(leaderboard_frame, text=str(rank)).grid(row=rank, column=0)
            tk.Label(leaderboard_frame, text=username).grid(row=rank, column=1)
            tk.Label(leaderboard_frame, text=difficulty).grid(row=rank, column=2)
            tk.Label(leaderboard_frame, text=f"{time:.2f}s").grid(row=rank, column=3)

        tk.Button(leaderboard_window, text="Close", command=leaderboard_window.destroy).pack(pady=10)


#difficulty menu 
    def show_difficulty_selection(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        tk.Label(self.menu_frame, text="Select Difficulty", font=('Arial', 18)).pack(pady=20)

        tk.Button(self.menu_frame, text="Easy", font=('Arial', 18), command=lambda: self.start_game("easy")).pack(pady=15, fill='x')
        tk.Button(self.menu_frame, text="Medium", font=('Arial', 18), command=lambda: self.start_game("medium")).pack(pady=15, fill='x')
        tk.Button(self.menu_frame, text="Hard", font=('Arial', 18), command=lambda: self.start_game("hard")).pack(pady=15, fill='x')

        tk.Button(self.menu_frame, text="Leaderboard", font=('Arial', 18), command=self.show_leaderboard).pack(pady=15, fill='x')

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

        # Destroy existing control frame if it exists
        if hasattr(self, 'control_frame'):
            self.control_frame.destroy()

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
        self.control_frame = tk.Frame(self.game_frame)
        self.control_frame.pack(side=tk.LEFT, fill='y')

        # Undo button
        tk.Button(self.control_frame, text="Undo", font=('Arial', 12),
                  command=self.undo_move).pack(pady=5)

        # New Game button
        tk.Button(self.control_frame, text="New Game", font=('Arial', 12),
                  command=self.return_to_menu).pack(pady=5)

        # Exit button
        tk.Button(self.control_frame, text="Exit", font=('Arial', 12),
                  command=self.root.quit).pack(pady=5)

        tk.Button(self.control_frame, text="Hint", font=('Arial', 12),
                  command=self.give_hint).pack(pady=5)

        # Timer label
        self.timer_label = tk.Label(self.control_frame, text="Time: 00:00", font=('Arial', 12))
        self.timer_label.pack(pady=10)

        # Bind arrow keys for navigation
        self.root.bind('<Up>', lambda e: self.navigate("Up"))
        self.root.bind('<Down>', lambda e: self.navigate("Down"))
        self.root.bind('<Left>', lambda e: self.navigate("Left"))
        self.root.bind('<Right>', lambda e: self.navigate("Right"))

    def give_hint(self):
        if self.selected:
            row, col = self.selected

            # Check if the cell is not an original cell and is empty
            if (row, col) not in self.original_cells and not self.cells[(row, col)].get():
                # Fill the cell with the correct value from the solution
                correct_value = self.solution[row][col]
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].insert(0, str(correct_value))
                self.cells[(row, col)].config(fg='green')  # Use a different color to indicate a hint
            else:
                messagebox.showinfo("Hint", "Please select an empty cell that you can modify.")
        else:
            messagebox.showinfo("Hint", "Please select a cell to use a hint.")

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
        
        # Calculate game time
        game_time = time.time() - self.start_time
        
        # Add score to leaderboard
        self.leaderboard_manager.add_score(self.current_user, self.difficulty, game_time)
        
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
                    time_message = f"Congratulations!!!\nYou solved the Sudoku! Your time is {minutes} minutes and {seconds} seconds."
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

        # Save start time for tracking game duration
        self.start_time = time.time()
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = SudokuGUI()
    game.run()
