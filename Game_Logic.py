import random
import time
import os


def is_valid_solution(row, col, num, cells):
    # Check row
    for j in range(9):
        if j != col and cells[(row, j)].get() == str(num):
            return False

    # Check column
    for i in range(9):
        if i != row and cells[(i, col)].get() == str(num):
            return False

    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if (i != row or j != col) and cells[(i, j)].get() == str(num):
                return False

    return True


def is_safe(grid, row, col, num):
    # Check row
    for x in range(9):
        if grid[row][x] == num or grid[x][col] == num:
            return False

    # Check 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[i + start_row][j + start_col] == num:
                return False

    return True


def fill_sudoku(grid):
    """Fill the Sudoku grid using backtracking and return the grid if successful."""
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:  # Find an empty cell
                numbers = list(range(1, 10))
                random.shuffle(numbers)  # Shuffle numbers for randomness
                for num in numbers:
                    if is_safe(grid, row, col, num):
                        grid[row][col] = num
                        if fill_sudoku(grid):
                            return grid
                        grid[row][col] = 0  # Backtrack
                return None  # Return None if no valid number can be placed
    return grid  # Return the filled grid when complete


def generate_filled_sudoku():
    """Generate a filled Sudoku grid."""
    grid = [[0] * 9 for _ in range(9)]
    return fill_sudoku(grid)


# def generate_puzzle(difficulty): # this function solution is bad because
# #returned grid has multiple solutions,  which contradicts to sudoku rules
#     # Create a solved Sudoku grid
#     grid = generate_filled_sudoku()
#     # Remove numbers based on difficulty
#     removes = {"easy": 40, "medium": 50, "hard": 60}
#     cells_to_remove = removes[difficulty]
#
#     coordinates = [(i, j) for i in range(9) for j in range(9)]
#     random.shuffle(coordinates)
#
#     for i, j in coordinates[:cells_to_remove]:
#         grid[i][j] = 0
#
#     return grid

def solve(grid, solutions_count, max_solutions=2):
    """Attempt to solve the Sudoku puzzle, stopping if more than one solution is found."""
    if solutions_count[0] > max_solutions:
        return
    # Find the next empty cell
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                # Try all numbers for this cell
                for num in range(1, 10):
                    if is_safe(grid, row, col, num):
                        grid[row][col] = num
                        solve(grid, solutions_count, max_solutions)  # Recurse
                        grid[row][col] = 0  # Backtrack
                        # if __name__ == "__main__":
                        #     print_grid(grid)
                        #     time.sleep(0.1)
                        #     os.system('clear')
                return
    solutions_count[0] += 1  # Found one solution


def generate_puzzle(difficulty):
    """Generate a Sudoku puzzle with a unique solution."""
    original_puzzle = generate_filled_sudoku()  # Start with a solved grid
    puzzle = [row[:] for row in original_puzzle]  # Deep copy the solved grid

    # Define removal counts based on difficulty
    removal_count = {"easy": 35, "medium": 45, "hard": 55}.get(difficulty, 45)

    # List of all cell indices (0 to 80)
    cells_to_remove = random.sample(range(81), removal_count)

    # Remove the values from the grid
    for idx in cells_to_remove:
        row, col = divmod(idx, 9)
        puzzle[row][col] = 0  # Set the value to 0 to "remove" it

    # Check for uniqueness once the grid is modified
    solutions_count = [0]
    solve([row[:] for row in puzzle], solutions_count)

    # If there is more than one solution, retry with a different set of removals
    attempts = 0
    max_attempts = 5  # Retry 5 times max

    while solutions_count[0] != 1 and attempts < max_attempts:
        puzzle = [row[:] for row in original_puzzle]  # Restore the grid
        cells_to_remove = random.sample(range(81), removal_count)
        for idx in cells_to_remove:
            row, col = divmod(idx, 9)
            puzzle[row][col] = 0  # Remove the value
        solutions_count = [0]
        solve([row[:] for row in puzzle], solutions_count)
        attempts += 1


    return puzzle, original_puzzle

def print_grid(grid):
    for row in grid:
        print(row)
    print("")




if __name__ == "__main__":
    generate_puzzle("hard")



