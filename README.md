*This project has been created as part of the 42 curriculum by aeuvrard, cjost.*

# A-Maze-ing

## Description

A-Maze-ing is a procedural maze generator written in **Python 3.10+**. It reads a configuration file, generates a random maze (perfect or imperfect), embeds a "42" pattern carved out of fully closed cells, computes the shortest path between entry and exit, renders the result in the terminal, and writes everything to an output file in a compact hexadecimal format.

The project is split into two parts:

- The **application** (`a_maze_ing.py` + `infrastructure/`) — parses the config, drives generation, renders the maze, and writes the output file.
- The **`mazegen` package** — a standalone, reusable library that can be built as a wheel and installed in another project. It exposes a single `MazeGenerator` facade.

### Features

- Recursive Backtracker (DFS) generation algorithm
- Perfect mazes (single unique path) or imperfect mazes (with loops)
- "42" pattern carved into the maze using fully closed cells
- BFS-based shortest-path solver
- Seed-based reproducibility (random seed if none provided, printed back so you can replay it)
- ANSI terminal rendering with color cycling and live interactivity
- Hexadecimal output file compatible with the project's validation script

---

## Instructions

### Requirements

- Python **3.10+**
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management
- GNU `make`

### Installation

```bash
make install
```

This creates a `uv`-managed virtual environment and installs the dependencies (Pydantic, flake8, mypy).

### Run

```bash
make run
```

Or, equivalently:

```bash
uv run python3 a_maze_ing.py config.txt
```

You can pass any configuration file path as the only argument.

### Other make targets

| Target | What it does |
|---|---|
| `make install` | Set up the virtualenv and install dependencies |
| `make run` | Run `a_maze_ing.py` with `config.txt` |
| `make debug` | Launch the main script under `pdb` |
| `make lint` | Run flake8 and mypy with the required flags |
| `make lint-strict` | Same as `lint` but with `mypy --strict` |
| `make build` | Build the `mazegen` wheel under `dist/` |
| `make clean` | Remove caches (`__pycache__`, `.mypy_cache`) |
| `make fclean` | Remove the virtualenv |
| `make help` | Print a short summary of the available targets |

### Validating the output

A validator script `output_validator.py` is provided to check the coherence of the hex grid (each wall must be declared identically by both neighbouring cells):

```bash
python3 output_validator.py maze.txt
```

It prints nothing on success, and reports `Wrong encoding for (x,y)` for any mismatched cell pair.

---

## Configuration file

The configuration file is plain text, with one `KEY=VALUE` pair per line. Blank lines and lines starting with `#` are ignored. Keys are case-insensitive; values are trimmed.

### Mandatory keys

| Key | Type | Constraints | Description |
|---|---|---|---|
| `WIDTH` | integer | `2 ≤ WIDTH ≤ 30` | Maze width in cells |
| `HEIGHT` | integer | `2 ≤ HEIGHT ≤ 30` | Maze height in cells |
| `ENTRY` | `x,y` | inside maze bounds | Entry coordinates (0-indexed) |
| `EXIT` | `x,y` | inside maze bounds, ≠ ENTRY | Exit coordinates (0-indexed) |
| `OUTPUT_FILE` | string | 1–20 characters | Path to the output file |
| `PERFECT` | boolean | `true`/`false`/`1`/`0`/`yes`/`no` | `true` = single path, `false` = with loops |

### Optional keys

| Key | Type | Default | Description |
|---|---|---|---|
| `SEED` | integer | random | Seed for reproducible generation. Leave empty or omit for random |

### Example configuration

```ini
# Maze dimensions
WIDTH=20
HEIGHT=15

# Entry and exit (0-indexed)
ENTRY=0,0
EXIT=19,14

# Output file
OUTPUT_FILE=maze.txt

# Perfect maze: True = unique path between entry and exit
PERFECT=true

# Optional: leave commented for a random seed
# SEED=42
```

A default `config.txt` is provided at the root of the repository.

---

## Maze generation algorithm

### Recursive Backtracker (DFS)

The maze is carved using a **randomised depth-first search** (also known as the recursive backtracker):

1. Pick a starting cell and push it onto a stack.
2. From the current cell, pick a random unvisited neighbour. If one exists, knock down the wall between them, push the new cell onto the stack, and continue from there.
3. If no unvisited neighbour exists, pop the stack and continue from the previous cell.
4. Stop when the stack is empty.

This always produces a **perfect maze** (a spanning tree of the cell grid: exactly one path between any two cells). When `PERFECT=false`, the generator then knocks down a small fraction of additional inner walls to introduce loops, while explicitly checking that no 3×3 fully open area is created.

The "42" pattern is reserved on the grid **before** carving starts: those cells are excluded from the DFS, so they remain fully closed (4 walls) and visually form the digits when rendered.

### Why this algorithm

We chose recursive backtracking because it is:

- **Simple to reason about** — a straightforward stack-based DFS with random neighbour selection.
- **Naturally produces perfect mazes** — no post-processing needed for the `PERFECT=true` case.
- **Well-suited for seeded reproducibility** — every random choice goes through one seeded RNG, so the same seed always yields the same maze.
- **Easy to integrate with reserved cells** — skipping the "42" cells is a one-line check in the neighbour selection step.

### Shortest path (BFS)

The solver uses a **breadth-first search** from entry to exit. BFS is the natural choice here because:

- The maze graph is unweighted (every step has cost 1).
- BFS guarantees the shortest path in the number of moves.
- It's straightforward to implement with a `collections.deque`.

The path is returned as a string of `N`/`E`/`S`/`W` moves and written to the output file.

---

## Display & interactive controls

The terminal renderer uses ANSI escape codes and reads single keystrokes via `termios` raw mode (no Enter needed). The "42" pattern, entry (green), exit (red), and walls/paths are all drawn with distinct colors.

| Key | Action |
|---|---|
| `s` | Show / hide the shortest path |
| `c` | Cycle through wall/path/solution color themes |
| `r` | Regenerate a new maze (with a new random seed) |
| `q` | Quit |

---

## Output file format

The output file follows the format defined in the subject:

```
<hex grid: one row per line, one hex digit per cell>

<entry x,y>
<exit x,y>
<shortest path: sequence of N/E/S/W>
```

Each hex digit encodes the cell's closed walls as a bitmask:

| Bit | Value | Direction |
|---|---|---|
| 0 (LSB) | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

A closed wall sets the bit to `1`. So `A` (binary `1010`) means east and west are closed; `F` (binary `1111`) means all four walls are closed (a reserved "42" cell).

Cells are written row by row, then a blank line, then the three trailing lines (entry, exit, path). All lines end with `\n`.

---

## Reusable module: `mazegen`

The reusable part of the project is the `mazegen` package, located at the root of the repository. It is fully independent from the rendering and config-parsing layers, and can be built as a wheel and installed elsewhere with `pip`.

A detailed README for the package is available at **[`mazegen/README.md`](./mazegen/README.md)**.

---

## Team & project management

### Team

- **aeuvrard** — Makefile, terminal renderer (ANSI + raw-mode input, color themes, interactive controls), shortest-path solver (BFS)
- **cjost** — Recursive Backtracker generator (DFS), `42` pattern injection, configuration model and parser (Pydantic-based), output file writer
- **both** — Project architecture and integration

### Planning

We allocated **two weeks** for the project and split the work along the natural seams of the architecture (generation / solving / rendering / config). We checked in regularly to make sure the data structures exchanged between modules stayed in sync — in particular the `Maze` and `Cell` entities, which are the contract between every layer.

The plan evolved in two main ways:

- The clean split between the **reusable `mazegen` package** and the **application layer** (config parser, file writer, renderer) emerged early on and made the rest of the work much easier. Both members could iterate on their part without stepping on each other.
- Renderer interactivity (raw-mode key handling, color cycling, redrawing) took a bit more iteration than expected, mostly because of terminal quirks rather than algorithmic complexity.

### What worked well

- **Clear separation between domain and infrastructure.** The `mazegen` package never imports anything from `infrastructure/`, which made the "build it as a wheel and reuse it" requirement essentially free.
- **Single source of randomness.** All random choices in the generator go through one seeded `random.Random` instance, so the same seed produces the exact same maze every time.
- **Pydantic for config validation.** Caught a lot of silly errors (bad coordinate format, out-of-bounds entry/exit, non-integer seeds) at parse time with clear messages, instead of crashing deep in the generator.

### What could be improved

- Add proper unit tests (`pytest`). For now the project was validated manually and via `output_validator.py`.
- Add CI to run flake8, mypy, and the validator automatically.
- Support a second generation algorithm (e.g. Prim's) for variety.
- A graphical renderer (MLX or pygame) would be a nice extension to the terminal one.

### Tools used

| Tool | Purpose |
|---|---|
| `uv` | Virtualenv and dependency management |
| `pydantic` | Configuration file validation |
| `flake8` | Style linting |
| `mypy` | Static type checking |
| `pdb` | Debugging (`make debug`) |
| ANSI escape codes + `termios` | Terminal rendering and raw-mode key input |
| Git | Version control |

---

## Resources

### References

- Recursive Backtracker explained step-by-step — Jamis Buck: <https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking>
- Maze generation algorithms overview — Wikipedia: <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- BFS vs DFS — GeeksForGeeks: <https://www.geeksforgeeks.org/dsa/difference-between-bfs-and-dfs/>
- DFS — GeeksForGeeks: <https://www.geeksforgeeks.org/dsa/depth-first-search-or-dfs-for-a-graph/>
- BFS — GeeksForGeeks: <https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/>
- Pydantic documentation: <https://docs.pydantic.dev/>
- ANSI escape codes — Wikipedia: <https://en.wikipedia.org/wiki/ANSI_escape_code>
- Python `typing` module: <https://docs.python.org/3/library/typing.html>

### AI usage

AI assistance (Claude) was used in a few targeted ways during development:

- **Debugging** — explaining cryptic error messages (Pydantic validation errors, `termios` flag combinations) and helping trace tricky bugs.
- **Docstrings** — drafting and polishing English docstrings across the codebase to keep them consistent in style.
- **Drafting parts of this README** — structuring the document and refining wording, with the content and project decisions coming from us.

In every case, AI-suggested code or text was reviewed, tested, and rewritten where needed. Nothing was committed that we couldn't explain on our own during the defense.