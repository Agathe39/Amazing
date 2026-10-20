"""Core domain entities for maze representation.

Defines the Cell and Maze dataclasses, plus the bitmask constants and
lookup tables used to represent cardinal directions and walls throughout
the project.

Wall encoding:
    Each Cell stores its closed walls as a 4-bit integer — bit 0 = North,
    bit 1 = East, bit 2 = South, bit 3 = West. A bit set to 1 means the
    wall is closed.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

NORTH: int = 0b0001
EAST: int = 0b0010
SOUTH: int = 0b0100
WEST: int = 0b1000

OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}

DIRECTION_DELTA: dict[int, Tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}

DIRECTION_LETTER: dict[int, str] = {
    NORTH: "N",
    EAST: "E",
    SOUTH: "S",
    WEST: "W",
}

DIRECTION_COORDINATES: dict[str, int] = {
    "N": NORTH,
    "E": EAST,
    "S": SOUTH,
    "W": WEST
}

ALL_WALLS: int = NORTH | EAST | SOUTH | WEST

WALLS: dict[int, str] = {
    0:  "N, E, S, W",
    1:  "E, S, W",
    2:  "N, S, W",
    3:  "S, W",
    4:  "N, E, W",
    5:  "E, W",
    6:  "N, W",
    7:  "W",
    8:  "N, E, S",
    9:  "E, S",
    10: "N, S",
    11: "S",
    12: "N, E",
    13: "E",
    14: "N",
}


@dataclass
class Cell:
    """A single maze cell with its four walls stored as a bitmask."""
    x: int
    y: int
    walls: int = ALL_WALLS
    visited: bool = False
    is_42_pattern: bool = False

    def has_wall(self, direction: int) -> bool:
        """Return True if the wall on `direction` is closed."""
        return bool(self.walls & direction)

    def remove_wall(self, direction: int) -> None:
        """Open (carve through) the wall on `direction`."""
        self.walls &= ~direction

    def add_wall(self, direction: int) -> None:
        """Close the wall on `direction`."""
        self.walls |= direction

    def hex_value(self) -> str:
        """Return the wall bitmask as a single uppercase hex digit."""
        return format(self.walls, "X")


@dataclass
class Maze:
    """A 2D grid of Cells with entry, exit and an optional solution path.

    Attributes:
        cells: 2D list indexed as cells[y][x].
        solution: List of N/E/S/W letters from entry to exit.
        seed: The seed that produced this maze, kept for reproducibility.
    """

    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    cells: List[List[Cell]] = field(default_factory=list)
    solution: List[str] = field(default_factory=list)
    seed: Optional[int] = None
    carving_history: List[Tuple[int, int]] = field(default_factory=list)

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at (x, y).

        Raises:
            IndexError: If (x, y) is outside the maze bounds.
        """
        if not self.in_bounds(x, y):
            raise IndexError(
                f"Cell ({x}, {y}) out of bounds ({self.width}x{self.height})"
            )
        return self.cells[y][x]

    def in_bounds(self, x: int, y: int) -> bool:
        """True if (x, y) lies inside the maze."""
        return 0 <= x < self.width and 0 <= y < self.height

    def to_hex_grid(self) -> List[str]:
        """Serialise the maze as one hex string per row, suitable
        for file output."""
        return [
            "".join(self.cells[y][x].hex_value() for x in range(self.width))
            for y in range(self.height)
        ]
