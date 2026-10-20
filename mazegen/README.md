# mazegen

A reusable Python module for generating, solving, and exporting random mazes,
featuring a built-in "42" pattern and a recursive-backtracker generator.

---

## Installation

Install the wheel from your project root:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

Or, after building from source:

```bash
make build
pip install dist/mazegen-*.whl
```

---

## Quick start

```python
from mazegen.facade import MazeGenerator

gen = MazeGenerator()
maze = gen.generate()

# Print the maze as a hex grid
for row in gen.get_hex_grid():
    print(row)

# Print the solution as N/E/S/W letters
print("".join(gen.get_solution_path()))
```

That's it. With no arguments, you get a 20×15 perfect maze with entry at
`(0, 0)`, exit at `(19, 14)`, and a random seed.

---

## Custom parameters

All constructor parameters are optional. The defaults handle the common case;
override anything you need:

```python
from mazegen.facade import MazeGenerator

gen = MazeGenerator(
    width=30,
    height=20,
    entry=(0, 0),
    exit_=(29, 19),
    seed=42,            # set for reproducibility, omit for random
    perfect=True,       # False adds loops (multiple paths)
)
maze = gen.generate()
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | `int` | `20` | Maze width in cells |
| `height` | `int` | `15` | Maze height in cells |
| `entry` | `Tuple[int, int]` | `(0, 0)` | Entry coordinates |
| `exit_` | `Tuple[int, int]` | `(width-1, height-1)` | Exit coordinates |
| `seed` | `Optional[int]` | random | Seed for reproducibility |
| `perfect` | `bool` | `True` | If `False`, ~14% of inner walls are removed to add loops |

### Reproducibility with seeds

Same seed → identical maze, every time:

```python
gen1 = MazeGenerator(seed=42)
gen2 = MazeGenerator(seed=42)
gen1.generate().to_hex_grid() == gen2.generate().to_hex_grid()  # True
```

If you don't pass a seed, one is generated for you. Read it back via
`gen.seed` so you can reproduce the maze later:

```python
gen = MazeGenerator()              # random seed
gen.generate()
print(f"This maze used seed: {gen.seed}")
```

---

## Accessing the generated structure

The generator exposes the maze through three accessors:

### 1. The full `Maze` object

```python
maze = gen.maze              # property — works after generate()

maze.width                   # int
maze.height                  # int
maze.entry                   # (x, y) tuple
maze.exit                    # (x, y) tuple
maze.cells                   # 2D list of Cell objects, indexed [y][x]
maze.solution                # list of "N"/"E"/"S"/"W" letters
maze.seed                    # the seed used
```

### 2. Hex grid (compact serialisation)

```python
grid = gen.get_hex_grid()
# Returns: List[str], one row per line, each character one hex digit.
# Each hex digit encodes which walls are closed:
#   bit 0 = N, bit 1 = E, bit 2 = S, bit 3 = W
# Example:
#   ['F', '5', '7', ...]   ← row by row
```

This is the format the project writes to the output file. Useful for
testing, debugging, or piping to another tool.

### 3. Solution path

```python
path = gen.get_solution_path()
# Returns: List[str] of N/E/S/W letters, one per step.
# Example: ['S', 'S', 'E', 'E', 'N', ...]
```

The path is computed automatically by `generate()` — no extra call needed.

---

## Inspecting individual cells

For finer-grained access, work with `Cell` objects directly:

```python
from mazegen.entities import NORTH, EAST, SOUTH, WEST

cell = maze.get_cell(5, 3)   # returns the Cell at (x=5, y=3)

cell.x, cell.y               # coordinates
cell.has_wall(NORTH)         # bool — is the north wall closed?
cell.has_wall(EAST)          # bool
cell.is_42_pattern           # bool — is this cell part of the "42"?
cell.hex_value()             # str — single hex digit ('0' to 'F')
```

The wall direction constants and their bit values:

| Constant | Bit | Hex |
|----------|-----|-----|
| `NORTH`  | `0b0001` | `1` |
| `EAST`   | `0b0010` | `2` |
| `SOUTH`  | `0b0100` | `4` |
| `WEST`   | `0b1000` | `8` |

A cell with all four walls closed has `walls == 0b1111 == 15` (`F` in hex).

---

## Full example

```python
from mazegen.facade import MazeGenerator

# Configure and generate
gen = MazeGenerator(width=10, height=10, seed=2024, perfect=False)
maze = gen.generate()

# Inspect
print(f"Seed: {gen.seed}")
print(f"Entry: {maze.entry}, Exit: {maze.exit}")
print(f"Solution length: {len(maze.solution)} steps")
print(f"Solution: {''.join(maze.solution)}")

# Print the grid
print("\nHex grid:")
for row in gen.get_hex_grid():
    print(f"  {row}")

# Walk through the cells
print("\nFirst row walls:")
for x in range(maze.width):
    cell = maze.get_cell(x, 0)
    print(f"  ({x}, 0): {cell.hex_value()} — pattern={cell.is_42_pattern}")
```

---

## Error handling

| Situation | Behaviour |
|-----------|-----------|
| `gen.maze` accessed before `generate()` | Raises `RuntimeError` |
| `maze.get_cell(x, y)` out of bounds | Raises `IndexError` |
| Maze too small for the "42" pattern | Pattern is silently skipped |

`generate()` itself never raises for valid arguments — invalid arguments
raise `ValueError` from the underlying use case (e.g. entry equals exit,
size below 2×2).

---

## Module structure (for reference)

```
mazegen/
├── facade.py              ← MazeGenerator (the public API)
├── entities.py            ← Maze, Cell, direction constants
├── algorithms/
│   ├── recursive_backtracker.py
│   └── pattern_42.py
└── use_cases/
    ├── generate_maze.py
    └── solve_maze.py
```

For typical use, importing only from `mazegen.facade` is enough.
Direct access to `mazegen.entities` is useful when inspecting cells or
working with the wall constants.