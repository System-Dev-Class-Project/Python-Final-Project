import tkinter as tk
from tkinter import messagebox
import Game_Logic
import time
import Play_Sound
import pygame

from LeaderboardManager import LeaderboardManager
from UserManager import UserManager


class SudokuGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sudoku")
        self.cells = {}
        self.selected = None
        self.original_cells = set()
        self.moves_history = []
        self.timer_running = False
        self.timer_job = None

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
        """Display the initial menu with Register, Log In, Play as Guest, and Leaderboard."""
        # Clear the menu frame
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        # Title
        title = tk.Label(self.menu_frame, text="SUDOKU", font=('Arial', 48, 'bold'), bg="#f0f0f0", fg="#000000")
        title.pack(pady=(20, 50))

        # Instructions
        subtitle = tk.Label(self.menu_frame, text="Select an option to get started",
                            font=('Arial', 18), bg="#f0f0f0", fg="#000000")
        subtitle.pack(pady=(0, 30))

        # Button Styles
        button_style = {
            'font': ('Arial', 18),
            'bg': '#4CAF50',
            'fg': '#000000',
            'activebackground': '#45a049',
            'activeforeground': '#000000',
            'relief': 'raised',
            'bd': 3,
            'cursor': 'hand2'
        }

        # Buttons
        tk.Button(self.menu_frame, text="Register", **button_style,
                  command=self.open_register_popup).pack(pady=10, fill='x', padx=20)
        tk.Button(self.menu_frame, text="Log In", **button_style,
                  command=self.open_login_popup).pack(pady=10, fill='x', padx=20)
        tk.Button(self.menu_frame, text="Play as Guest", **button_style,
                  command=self.start_as_guest).pack(pady=10, fill='x', padx=20)
        tk.Button(self.menu_frame, text="Leaderboard", **button_style,
                  command=self.show_leaderboard).pack(pady=10, fill='x', padx=20)

        # Exit button
        exit_button_style = button_style.copy()
        exit_button_style.update({'bg': '#f44336', 'activebackground': '#e53935'})
        tk.Button(self.menu_frame, text="Exit", **exit_button_style,
                  command=self.root.quit).pack(pady=(30, 10), fill='x', padx=20)



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
        """Display the difficulty selection menu after a user logs in or chooses to play as a guest."""
        # Clear the menu frame
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        # Title
        title = tk.Label(self.menu_frame, text="Select Difficulty", font=('Arial', 24, 'bold'))
        title.pack(pady=40)

        # Difficulty Buttons
        tk.Button(self.menu_frame, text="Easy", font=('Arial', 18),
                  command=lambda: self.start_game("easy")).pack(pady=15, fill='x')
        tk.Button(self.menu_frame, text="Medium", font=('Arial', 18),
                  command=lambda: self.start_game("medium")).pack(pady=15, fill='x')
        tk.Button(self.menu_frame, text="Hard", font=('Arial', 18),
                  command=lambda: self.start_game("hard")).pack(pady=15, fill='x')

        # Back to main menu button
        tk.Button(self.menu_frame, text="Back to Main Menu", font=('Arial', 18),
                  command=self.create_menu).pack(pady=30)



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
            self.timer_job = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def return_to_menu(self):
        # Stop ticking sound
        pygame.mixer.Channel(2).stop()
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
                    Play_Sound.play_victory()
                    time_message = f"Congratulations!!!\nYou solved the Sudoku! Your time is {minutes} minutes and {seconds} seconds."
                    messagebox.showinfo("Congratulations!", time_message)
                    self.return_to_menu()
            else:
                # Mark invalid move with red background
                self.cells[self.selected].delete(0, tk.END)
                self.cells[self.selected].insert(0, event.char)
                self.cells[self.selected].config(bg='pink')
                # Play sound
                Play_Sound.play_wrong_move()

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
        
        # Stop any active timers
        self.stop_timer()
        
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
        
        # Play sounds
        Play_Sound.play_new_game()
        Play_Sound.play_ticking()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = SudokuGUI()
    game.run()