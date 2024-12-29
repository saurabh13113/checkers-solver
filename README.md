# ♟️ Game Tree Search: Checkers Endgame Solver

## 📖 Overview
This project implements a solver for Checkers endgame puzzles using advanced search techniques like alpha-beta pruning, node ordering, and state caching. Learn more about the fascinating history of Checkers AI in this [article](https://en.wikipedia.org/wiki/Solved_game#Checkers).

---

## 🎮 Game Rules

### 🛠️ Basics:
- **Board:** 8x8 grid, dark squares are playable.
- **Players:** Red and Black (Red always moves first).
- **Piece Types:**
  - `r`: Red piece (moves forward diagonally).
  - `b`: Black piece (moves forward diagonally).
  - `R`: Red King (moves diagonally in all directions).
  - `B`: Black King (moves diagonally in all directions).

### 🔄 Moves:
1. **Simple Move:** A piece moves one square diagonally to an adjacent unoccupied square.
2. **Jump:** A piece jumps over an opponent's adjacent piece into an empty square, capturing it. 
   - **Mandatory Jumping:** If a jump is available, it must be made.
   - **Multiple Jumps:** After one jump, a piece must continue jumping as long as possible.

### 👑 Kings:
- A piece reaching the last row becomes a king, gaining backward movement.
- Multi-jumps stop after a piece becomes a king; subsequent moves can resume jumping.

### 🎯 End of Game:
- A player wins by capturing all the opponent's pieces or when the opponent has no legal moves left.

![image](https://github.com/user-attachments/assets/2bb61964-ca8e-40a6-a55b-4e063a54fd9e)


## 💼 Features

### 🎯 Your Tasks:
- Implement **alpha-beta pruning** and other optimizations for efficient game tree exploration.
- Ensure optimal move selection for both players:
  - **Winning player:** Minimizes moves to win.
  - **Losing player:** Maximizes moves to delay defeat.

### 🔍 Search Optimizations:
1. **Alpha-Beta Pruning:** Reduces the number of nodes evaluated in the game tree.
2. **Node Ordering:** Explores better moves first to improve pruning efficiency.
3. **State Caching:** Memorizes previously evaluated states for faster lookups.

---

## 🚀 How to Run

### Prerequisites
- **Python 3**: Ensure Python 3 is installed on your system.

### Commands
To solve a Checkers puzzle:
```bash
python3 checkers.py --inputfile <input file> --outputfile <output file>
```

## 🧩 Input & Output Format
### Input:
Grid Representation:
.: Empty square.
r: Red piece.
b: Black piece.
R: Red King.
B: Black King.
The input file contains one initial board state.

Example Input:
........
....b...
.......R
..b.b...
...b...r
........
...r....
....B...

### Output:
The sequence of board states until the game ends.
States are separated by an empty line.

Example Output:
solution1.txt:
........
....b...
...R....
..b.b...
...b....
........
........
........


