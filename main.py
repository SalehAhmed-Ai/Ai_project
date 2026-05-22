import tkinter as tk
from collections import deque
import heapq
import random

GRID_SIZE = 10
CELL_SIZE = 50
WALL_PERCENTAGE = 0.25  # Adjusted to be balanced for board size

class MazeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Maze Solver - AI Search Visualization")

        self.start = (0, 0)
        self.goal = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.player = self.start
        self.player_path = [self.start]
        self.current_algorithm = ""

        self.generate_walls()

        self.canvas = tk.Canvas(root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
        self.canvas.pack()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Restart", command=self.restart).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Solve BFS", command=self.solve_bfs).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Solve DFS", command=self.solve_dfs).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Solve A*", command=self.solve_astar).grid(row=0, column=3, padx=5)

        root.bind("<Up>", lambda e: self.move(-1, 0))
        root.bind("<Down>", lambda e: self.move(1, 0))
        root.bind("<Left>", lambda e: self.move(0, -1))
        root.bind("<Right>", lambda e: self.move(0, 1))

        self.draw_grid()
        self.draw_player()

    def shortest_path_length(self, start, goal):
        """Return shortest path length in steps using BFS, or None if unreachable."""
        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            node, dist = queue.popleft()
            if node == goal:
                return dist
            for neighbor in self.safe_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        return None

    def show_victory_popup(self, winner, path_length):
        popup = tk.Toplevel(self.root)
        popup.title("Victory!")
        popup.geometry("300x180")
        popup.configure(bg="#1e1e1e")
        popup.grab_set()

        tk.Label(popup, text="🎉 GOAL REACHED! 🎉", font=("Arial", 14, "bold"), fg="#FFD54F", bg="#1e1e1e").pack(pady=10)
        tk.Label(popup, text=f"{winner} Path Length: {path_length}", font=("Arial", 12), fg="white", bg="#1e1e1e").pack(pady=5)

        tk.Button(popup, text="OK", bg="#4CAF50", fg="white", width=10, command=lambda: [popup.destroy(), self.restart()]).pack(pady=15)

    def restart(self):
        self.player = self.start
        self.player_path = [self.start]
        self.generate_walls()
        self.draw_grid()
        self.draw_player()

    def generate_walls(self):
        safe_zone = {self.start, (0,1), (1,0), self.goal, (GRID_SIZE-1, GRID_SIZE-2), (GRID_SIZE-2, GRID_SIZE-1)}
        while True:
            self.walls = set()
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if (r,c) in safe_zone:
                        continue
                    if random.random() < WALL_PERCENTAGE:
                        self.walls.add((r,c))
            if self.is_solvable():
                break

    def is_solvable(self):
        queue = deque([self.start])
        visited = set()
        while queue:
            node = queue.popleft()
            if node == self.goal:
                return True
            if node in visited:
                continue
            visited.add(node)
            for n in self.safe_neighbors(node):
                queue.append(n)
        return False

    def safe_neighbors(self, node):
        r,c = node
        moves = [(1,0),(-1,0),(0,1),(0,-1)]
        return [(r+dr,c+dc) for dr,dc in moves if 0<=r+dr<GRID_SIZE and 0<=c+dc<GRID_SIZE and (r+dr,c+dc) not in self.walls]

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1, x2, y2 = c*CELL_SIZE, r*CELL_SIZE, (c+1)*CELL_SIZE, (r+1)*CELL_SIZE
                color = "white"
                if (r,c) in self.walls:
                    color = "black"
                if (r,c) in self.player_path:
                    color = "#BDBDBD"
                if (r,c) == self.start:
                    color = "#8BC34A"  # light green start
                if (r,c) == self.goal:
                    color = "blue"  # goal
                self.canvas.create_rectangle(x1,y1,x2,y2,fill=color,outline="gray")

    def draw_player(self):
        r,c = self.player
        x, y = c*CELL_SIZE + CELL_SIZE//2, r*CELL_SIZE + CELL_SIZE//2
        self.canvas.create_oval(x-10,y-10,x+10,y+10,fill="yellow")

    def move(self, dr, dc):
        r,c = self.player
        nr,nc = r+dr,c+dc
        if 0<=nr<GRID_SIZE and 0<=nc<GRID_SIZE and (nr,nc) not in self.walls:
            self.player = (nr,nc)
            self.player_path.append(self.player)
            self.draw_grid()
            self.draw_player()
            if self.player == self.goal:
                # Count unique progress path for a fairer comparison against algorithms.
                path_length = self.shortest_path_length(self.start, self.goal)
                if path_length is None:
                    path_length = len(self.player_path) - 1
                self.show_victory_popup("Player", path_length)

    def animate_path(self, path):
        self.player_path = [self.start]
        for step in path:
            self.player = step
            self.player_path.append(step)
            self.draw_grid()
            self.draw_player()
            self.root.update()
            self.root.after(150)
        path_length = len(path)
        self.show_victory_popup(self.current_algorithm, path_length)
# -------- BFS -------- #
    def solve_bfs(self):
        self.current_algorithm = "BFS"
        queue = deque([(self.start, [])])
        visited = {self.start}
        while queue:
            node,path = queue.popleft()
            if node == self.goal:
                self.animate_path(path)
                return
            for n in self.safe_neighbors(node):
                if n not in visited:
                    visited.add(n)
                    queue.append((n, path+[n]))
# -------- DFS -------- #
    def solve_dfs(self):
        self.current_algorithm = "DFS"
        stack = [(self.start, [])]
        visited = {self.start}
        while stack:
            node,path = stack.pop()
            if node == self.goal:
                self.animate_path(path)
                return
            for n in self.safe_neighbors(node):
                if n not in visited:
                    visited.add(n)
                    stack.append((n, path+[n]))
# -------- A* -------- #
    def solve_astar(self):
        self.current_algorithm = "A*"
        open_set = []
        heapq.heappush(open_set,(0, self.start, []))
        best_g = {self.start: 0}
        while open_set:
            cost, node, path = heapq.heappop(open_set)
            if node == self.goal:
                self.animate_path(path)
                return
            g_current = len(path)
            if g_current > best_g.get(node, float("inf")):
                continue
            for n in self.safe_neighbors(node):
                g = g_current + 1
                if g < best_g.get(n, float("inf")):
                    best_g[n] = g
                    # use Manhattan Distance
                    h = abs(n[0]-self.goal[0]) + abs(n[1]-self.goal[1])
                    heapq.heappush(open_set, (g + h, n, path + [n]))

if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()