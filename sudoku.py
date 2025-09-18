# Sudoku problems.
# The CSP.ac_3() and CSP.backtrack() methods need to be implemented

from csp import CSP, alldiff
import time


def print_solution(solution):
    """
    Convert the representation of a Sudoku solution, as returned from
    the method CSP.backtracking_search(), into a Sudoku board.
    """
    for row in range(width):
        for col in range(width):
            print(solution[f'X{row+1}{col+1}'], end=" ")
            if col == 2 or col == 5:
                print('|', end=" ")
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')


# Choose Sudoku problem
file = "sudoku_hard.txt"

grid = open(file).read().split()

width = 9
box_width = 3

domains = {}
for row in range(width):
    for col in range(width):
        if grid[row][col] == '0':
            domains[f'X{row+1}{col+1}'] = set(range(1, 10))
        else:
            domains[f'X{row+1}{col+1}'] = {int(grid[row][col])}

edges = []
for row in range(width):
    edges += alldiff([f'X{row+1}{col+1}' for col in range(width)])
for col in range(width):
    edges += alldiff([f'X{row+1}{col+1}' for row in range(width)])
for box_row in range(box_width):
    for box_col in range(box_width):
        cells = []
        edges += alldiff(
            [
                f'X{row+1}{col+1}' for row in range(box_row * box_width, (box_row + 1) * box_width)
                for col in range(box_col * box_width, (box_col + 1) * box_width)
            ]
        )

csp = CSP(
    variables=[f'X{row+1}{col+1}' for row in range(width) for col in range(width)],
    domains=domains,
    edges=edges,
)


# Expected output after implementing csp.ac_3() and csp.backtracking_search():
# True
# 7 8 4 | 9 3 2 | 1 5 6
# 6 1 9 | 4 8 5 | 3 2 7
# 2 3 5 | 1 7 6 | 4 8 9
# ------+-------+------
# 5 7 8 | 2 6 1 | 9 3 4
# 3 4 1 | 8 9 7 | 5 6 2
# 9 2 6 | 5 4 3 | 8 7 1
# ------+-------+------
# 4 5 3 | 7 2 9 | 6 1 8
# 8 6 2 | 3 1 4 | 7 9 5
# 1 9 7 | 6 5 8 | 2 4 3
def print_domains_as_grid(domains, width=9, box_width=3):
    for row in range(width):
        for col in range(width):
            key = f'X{row+1}{col+1}'
            cell = ''.join(str(x) for x in sorted(domains[key]))
            print(f"{cell:9}", end=' ')
            if (col + 1) % box_width == 0 and col < width - 1:
                print('|', end=' ')
        print()
        if (row + 1) % box_width == 0 and row < width - 1:
            print('-' * (width * 9 + 6))  


start_total = time.time()
ac3_result = csp.ac_3()

print("Running Soduku:" + file)
print("AC-3 result:", ac3_result)
print("Domains after AC-3:")
print_domains_as_grid(csp.domains_after_ac3)

solution = csp.backtracking_search()
backtrack_runtime = csp.backtrack_runtime

print("Backtrack result:")
print_solution(solution)

print("Benchmark result:")
print(f"Backtracking calls: {csp.backtrack_calls}")
print(f"Backtracking failures: {csp.backtrack_failures}")
print(f"Backtracking runtime: {backtrack_runtime:.6f} seconds")
print(f"Total runtime (AC-3 + Backtracking): {time.time() - start_total:.6f} seconds")
