"""Recursive-backtracker maze generator.

Builds a perfect maze (single path between any two cells) by depth-first
carving from a random starting cell. Optionally adds loops afterwards
to produce an imperfect maze, while preventing 3x3 open areas.
"""

import random
from typing import List, Optional, Set, Tuple

from mazegen.entities import (
    ALL_WALLS,
    DIRECTION_DELTA,
    NORTH, EAST, SOUTH, WEST,
    OPPOSITE,
    Cell,
    Maze,
)


class RecursiveBacktrackerGenerator:
    def generate(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        seed: int,
        perfect: bool,
        reserved: Optional[Set[Tuple[int, int]]] = None,
    ) -> Maze:
        """Build and return a fully carved Maze.

        Args:
            seed: Drives an isolated random.Random instance — same seed
                always produces the same maze.
            perfect: If False, extra walls are removed to add loops.
            reserved: Cells that must not be carved into (used for the
                '42' pattern). They are walled off at the end.
        """

        rng = random.Random(seed)
        blocked: Set[Tuple[int, int]] = reserved or set()

        cells = self._init_cells(width, height)
        self._apply_border_walls(cells, width, height)
        carving_history = self._carve_passages(cells, width,
                                               height, rng, blocked)

        if not perfect:
            self._add_loops(cells, width, height, rng, blocked)

        for x, y in blocked:
            if 0 <= x < width and 0 <= y < height:
                cells[y][x].walls = ALL_WALLS
                cells[y][x].is_42_pattern = True
                for direction, (dx, dy) in DIRECTION_DELTA.items():
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        cells[ny][nx].add_wall(OPPOSITE[direction])

        return Maze(
            width=width,
            height=height,
            entry=entry,
            exit=exit_,
            cells=cells,
            seed=seed,
            carving_history=carving_history
        )

    @staticmethod
    def _init_cells(width: int, height: int) -> List[List[Cell]]:
        """Create a 2D grid of cells with all four walls closed."""
        return [
            [Cell(x=x, y=y, walls=ALL_WALLS) for x in range(width)]
            for y in range(height)
        ]

    @staticmethod
    def _apply_border_walls(
        cells: List[List[Cell]], width: int, height: int
    ) -> None:
        """Force outer walls on the four borders of the grid."""
        for x in range(width):
            cells[0][x].add_wall(NORTH)
            cells[height - 1][x].add_wall(SOUTH)
        for y in range(height):
            cells[y][0].add_wall(WEST)
            cells[y][width - 1].add_wall(EAST)

    def _carve_passages(
        self,
        cells: List[List[Cell]],
        width: int,
        height: int,
        rng: random.Random,
        blocked: Set[Tuple[int, int]],
    ) -> List[Tuple[int, int]]:
        """Iterative DFS carve from a random unblocked starting cell.

        At each step, picks a random unvisited neighbour and removes the
        wall between them. Backtracks via stack-pop when no neighbour is
        available. Stops once every non-blocked cell has been visited.
        """
        start_x, start_y = (rng.randint(0, width - 1),
                            rng.randint(0, height - 1))
        while (start_x, start_y) in blocked:
            start_x, start_y = (rng.randint(0, width - 1),
                                rng.randint(0, height - 1))

        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        passage_history: List[Tuple[int, int]] = [(start_x, start_y)]
        cells[start_y][start_x].visited = True
        visited_count = 1
        total = width * height - len(blocked)
        directions = [NORTH, EAST, SOUTH, WEST]

        while stack and visited_count < total:
            cx, cy = stack[-1]
            neighbors = self._unvisited_neighbors(
                cells, cx, cy, width, height, directions, blocked
            )
            if not neighbors:
                stack.pop()
                continue
            direction, (nx, ny) = rng.choice(neighbors)
            self._remove_wall(cells, cx, cy, direction, nx, ny)
            cells[ny][nx].visited = True
            visited_count += 1
            stack.append((nx, ny))
            passage_history.append((nx, ny))
        return passage_history

    @staticmethod
    def _unvisited_neighbors(
        cells: List[List[Cell]],
        cx: int,
        cy: int,
        width: int,
        height: int,
        directions: List[int],
        blocked: Set[Tuple[int, int]],
    ) -> List[Tuple[int, Tuple[int, int]]]:
        """Return (direction, (nx, ny)) tuples for in-bounds, unvisited,
        unblocked neighbours."""
        result: List[Tuple[int, Tuple[int, int]]] = []
        for direction in directions:
            dx, dy = DIRECTION_DELTA[direction]
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if not cells[ny][nx].visited and (nx, ny) not in blocked:
                    result.append((direction, (nx, ny)))
        return result

    @staticmethod
    def _remove_wall(
        cells: List[List[Cell]],
        cx: int,
        cy: int,
        direction: int,
        nx: int,
        ny: int,
    ) -> None:
        """Carve a passage by removing the wall on both sides."""
        cells[cy][cx].remove_wall(direction)
        cells[ny][nx].remove_wall(OPPOSITE[direction])

    def _add_loops(
        self,
        cells: List[List[Cell]],
        width: int,
        height: int,
        rng: random.Random,
        blocked: Set[Tuple[int, int]],
    ) -> None:
        """Remove ~1/7 of the remaining inner walls to add loops.

        Each candidate wall is removed only if it does not create a 3x3
        open area; otherwise the wall is restored.
        """
        candidates: List[Tuple[int, int, int]] = []
        for y in range(height):
            for x in range(width):
                if (x, y) in blocked:
                    continue
                east_ok = x + 1 < width and (x + 1, y) not in blocked
                if east_ok and cells[y][x].has_wall(EAST):
                    candidates.append((x, y, EAST))
                south_ok = y + 1 < height and (x, y + 1) not in blocked
                if south_ok and cells[y][x].has_wall(SOUTH):
                    candidates.append((x, y, SOUTH))

        rng.shuffle(candidates)
        target = max(1, len(candidates) // 7)
        removed = 0

        for x, y, direction in candidates:
            if removed >= target:
                break
            dx, dy = DIRECTION_DELTA[direction]
            nx, ny = x + dx, y + dy
            self._remove_wall(cells, x, y, direction, nx, ny)

            if self._has_large_open_area(cells, width, height, x, y) or \
               self._has_large_open_area(cells, width, height, nx, ny):
                cells[y][x].add_wall(direction)
                cells[ny][nx].add_wall(OPPOSITE[direction])
            else:
                removed += 1

    def _has_large_open_area(
        self,
        cells: List[List[Cell]],
        width: int,
        height: int,
        cx: int,
        cy: int,
    ) -> bool:
        """Return True if (cx, cy) is part of any 3x3 fully-open square."""
        s = 3
        for oy in range(cy - s + 1, cy + 1):
            for ox in range(cx - s + 1, cx + 1):
                if ox < 0 or oy < 0:
                    continue
                if ox + s > width or oy + s > height:
                    continue
                if self._is_open_square(cells, ox, oy, s):
                    return True
        return False

    @staticmethod
    def _is_open_square(
        cells: List[List[Cell]], ox: int, oy: int, size: int
    ) -> bool:
        """True if all interior walls within
        the square at (ox, oy) are open."""
        for y in range(oy, oy + size):
            for x in range(ox, ox + size):
                cell = cells[y][x]
                if x + 1 < ox + size and cell.has_wall(EAST):
                    return False
                if y + 1 < oy + size and cell.has_wall(SOUTH):
                    return False
        return True
