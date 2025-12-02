
# Labyrinth A* / Dijkstra with Fire

Mini-project on pathfinding in a maze modeled as a state graph, with:

- Dijkstra (A* with zero heuristic),
- A* with **Manhattan** heuristic,
- A* with **Euclidean** heuristic,
- **dynamic**, **static**, or **no** fire.

---

## Project Structure

```text
.
├── Main.py          # GUI (PySide6) + scenario management
├── Algorithm.py     # A* / Dijkstra + fire handling
├── MapGenerator.py  # Random maze generator (0/1)
└── __pycache__/     # Auto-generated Python cache files
```

---

## Requirements & Installation

- Python ≥ 3.9  
- PySide6

Install dependencies:

```bash
pip install PySide6
```

---

## How to Run

From the project directory:

```bash
python Main.py
```

A window opens with:

- left: maze visualization,
- right: controls and result panel.

---

## Scenario Types

Top right:

- **Random maze**  
  - Choose the **number of tests**.  
  - Each test:
    - generates a 0/1 maze,
    - places `D` (start) and `S` (exit),
    - adds between **1 and 3** fire sources `F`.

- **I define my maze**  
  - Choose the number of tests.  
  - For each test:
    - choose `N` (rows) and `M` (columns),
    - enter `N` lines of `M` characters using only:  
      `.` (free), `#` (wall), `D` (start), `S` (exit), `F` (fire).

For each test the UI shows: `Test i/n` and the results of all algorithms.

---

## Algorithms & Output

Algorithm buttons:

- **Dijkstra**
- **Manhattan**
- **Euclidean**

For each algorithm, the program displays:

- `Result: Y` if a **safe** path to `S` exists,
- `Result: N` otherwise,
- number of **explored nodes**,
- **execution time** in milliseconds.

Changing algorithm automatically recomputes the paths and restarts the animation.

---

## Fire Modes

- **Dynamic fire**  
  Fire spreads over time. A* ensures the prisoner never steps into a cell that is already on fire at the arrival time.

- **Static fire**  
  All `F` cells are treated as walls `#`.  
  This can make the maze disconnected (no path from `D` to `S`).

- **Remove fire**  
  All `F` cells become free cells `.`.  
  Fire is completely ignored (pure pathfinding benchmark).

Key messages are also printed to the console, for example:

- successful escape:  
  `The prisoner escapes successfully at t=..., position=(x,y), algorithm=...`
- blocked maze:  
  `[INFO] No path is possible for this test (fire mode = ...). Maze is blocked.`

---

## Color Legend

- **Black**: wall `#`
- **White**: free cell `.`
- **Green**: start `D` + trail (visited path)
- **Blue**: current position of the prisoner
- **Red**: exit `S`
- **Orange**: fire cell (`F` or cells reached by fire in dynamic mode)
