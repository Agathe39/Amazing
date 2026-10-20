"""Injects the '42' pattern into a generated maze.

The pattern is built from two 3x5 digit templates ('4' and '2') with a 1-cell
gap between them, surrounded by a 1-cell margin. Reserved cells are walled-off
and marked with `is_42_pattern=True` for the renderer to display them
distinctly.
"""

from collections import deque
from typing import List, Set, Tuple

from mazegen.entities import (
    ALL_WALLS,
    DIRECTION_DELTA,
    OPPOSITE,
    Maze,
)

_DIGIT_4: List[List[int]] = [
    [1, 0, 0],
    [1, 0, 0],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

_DIGIT_2: List[List[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

_ROWS = 5
_COLS = 3
_GAP = 1
_MARGIN = 1

_MIN_WIDTH = (_COLS * 2 + _GAP) + _MARGIN * 2
_MIN_HEIGHT = _ROWS + _MARGIN * 2


class Pattern42Injector:
    """Reserves and walls-off the cells forming the '42' pattern in a maze."""
    def inject(self, maze: Maze) -> bool:
        """Wall off the '42' cells in `maze` if it is large enough.

        Cells lying on the maze's solution path are skipped to keep the
        maze solvable.

        Returns:
            True if at least one cell was successfully walled off,
            False if the maze was too small or the pattern could not fit.
        """

        if maze.width < _MIN_WIDTH or maze.height < _MIN_HEIGHT:
            return False

        pattern_cells = self._build_pattern_cells(maze.width, maze.height)

        if maze.entry in pattern_cells or maze.exit in pattern_cells:
            raise ValueError("Entry or exit cannot be on the 42 pattern")
        if not self._fits(pattern_cells, maze.width, maze.height):
            return False

        solution_set = self._find_solution_path(maze)
        safe_cells = pattern_cells - solution_set

        for x, y in safe_cells:
            cell = maze.get_cell(x, y)
            cell.walls = ALL_WALLS
            cell.is_42_pattern = True
            self._sync_neighbors(maze, x, y)

        return bool(safe_cells)

    @staticmethod
    def _build_pattern_cells(
        width: int, height: int
    ) -> Set[Tuple[int, int]]:
        """Compute the set of (x, y) cells forming the centred '42' pattern.

        Raises:
            ValueError: If entry or exit lands on a pattern cell.
        """
        pattern_w = (_COLS * 2) + _GAP
        pattern_h = _ROWS

        start_x = (width - pattern_w) // 2
        start_y = (height - pattern_h) // 2

        cells: Set[Tuple[int, int]] = set()
        for digit_idx, digit in enumerate([_DIGIT_4, _DIGIT_2]):
            offset_x = digit_idx * (_COLS + _GAP)
            for row_idx, row in enumerate(digit):
                for col_idx, filled in enumerate(row):
                    if not filled:
                        continue
                    cx = start_x + offset_x + col_idx
                    cy = start_y + row_idx
                    cells.add((cx, cy))
        return cells

    @staticmethod
    def _fits(cells: Set[Tuple[int, int]], width: int, height: int) -> bool:
        """Check that every pattern cell respects the 1-cell margin."""
        return all(
            _MARGIN <= x < width - _MARGIN and _MARGIN <= y < height - _MARGIN
            for x, y in cells
        )

    @staticmethod
    def _find_solution_path(maze: Maze) -> Set[Tuple[int, int]]:
        """BFS from entry to exit; returns the cells on the shortest path."""
        visited: Set[Tuple[int, int]] = {maze.entry}
        queue: deque[Tuple[Tuple[int, int], List[Tuple[int, int]]]] = deque(
            [(maze.entry, [maze.entry])]
        )
        while queue:
            current, path = queue.popleft()
            if current == maze.exit:
                return set(path)
            cx, cy = current
            cell = maze.get_cell(cx, cy)
            for direction, (dx, dy) in DIRECTION_DELTA.items():
                if cell.has_wall(direction):
                    continue
                nb: Tuple[int, int] = (cx + dx, cy + dy)
                if nb not in visited and maze.in_bounds(nb[0], nb[1]):
                    visited.add(nb)
                    queue.append((nb, path + [nb]))
        return set()

    @staticmethod
    def _sync_neighbors(maze: Maze, x: int, y: int) -> None:
        """Add the matching opposite wall to each in-bounds neighbour.

        Keeps wall data consistent: if cell (x, y) has its east wall, the
        cell to its east must have its west wall.
        """
        for direction, (dx, dy) in DIRECTION_DELTA.items():
            nx, ny = x + dx, y + dy
            if maze.in_bounds(nx, ny):
                maze.get_cell(nx, ny).add_wall(OPPOSITE[direction])
