import tkinter as tk
from tkinter import messagebox
import random
import copy

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

    def create_game_ui(self):
        # Clear menu frame
        self.menu_frame.pack_forget()
        
        # Setup game frame
        self.game_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create grid
        self.grid_frame = tk.Frame(self.game_frame, bg='black')
        self.grid_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Create cells
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

    def return_to_menu(self):
        self.game_frame.pack_forget()
        self.menu_frame.pack(expand=True, fill='both')
        self.moves_history = []
        self.original_cells = set()

    def cell_selected(self, row, col):
        self.selected = (row, col)
        
    def key_pressed(self, event):
        if self.selected and event.char in '123456789':
            row, col = self.selected
            if (row, col) not in self.original_cells and self.is_valid_move(row, col, int(event.char)):
                # Store move in history
                old_value = self.cells[self.selected].get()
                self.moves_history.append((row, col, old_value))
                
                # Update cell
                self.cells[self.selected].delete(0, tk.END)
                self.cells[self.selected].insert(0, event.char)
                
                # Check if game is won
                if self.check_win():
                    messagebox.showinfo("Congratulations!", "You solved the Sudoku!")
                    self.return_to_menu()
            else:
                if (row, col) in self.original_cells:
                    messagebox.showwarning("Invalid Move", "Cannot modify original numbers!")
                else:
                    messagebox.showwarning("Invalid Move", "This number cannot be placed here!")
        return "break"  # Prevent default behavior
    
    def undo_move(self):
        if self.moves_history:
            row, col, value = self.moves_history.pop()
            self.cells[(row, col)].delete(0, tk.END)
            if value:
                self.cells[(row, col)].insert(0, value)

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

    def check_win(self):
        # Check if all cells are filled correctly
        for i in range(9):
            for j in range(9):
                value = self.cells[(i, j)].get()
                if not value or not self.is_valid_solution(i, j, int(value)):
                    return False
        return True
    
    def is_valid_solution(self, row, col, num):
        # Check row
        for j in range(9):
            if j != col and self.cells[(row, j)].get() == str(num):
                return False
                
        # Check column
        for i in range(9):
            if i != row and self.cells[(i, col)].get() == str(num):
                return False
                
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.cells[(i, j)].get() == str(num):
                    return False
        
        return True

    def generate_puzzle(self, difficulty):
        # Create a solved Sudoku grid
        grid = [[0 for _ in range(9)] for _ in range(9)]
        self.fill_grid(grid)
        
        # Remove numbers based on difficulty
        removes = {"easy": 40, "medium": 50, "hard": 60}
        cells_to_remove = removes[difficulty]
        
        coordinates = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(coordinates)
        
        for i, j in coordinates[:cells_to_remove]:
            grid[i][j] = 0
            
        return grid

    def fill_grid(self, grid):
        numbers = list(range(1, 10))
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    random.shuffle(numbers)
                    for num in numbers:
                        if self.is_safe(grid, i, j, num):
                            grid[i][j] = num
                            if self.fill_grid(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True

    def is_safe(self, grid, row, col, num):
        # Check row
        for x in range(9):
            if grid[row][x] == num:
                return False
        
        # Check column
        for x in range(9):
            if grid[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[i + start_row][j + start_col] == num:
                    return False
        
        return True

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.create_game_ui()
        
        # Generate new puzzle
        puzzle = self.generate_puzzle(difficulty)
        
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