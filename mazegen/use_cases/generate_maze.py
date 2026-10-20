"""Use case orchestrating maze generation, '42' pattern reservation,
and solving.

Acts as the application-layer entry point: takes raw parameters, coordinates
the generator, pattern injector and solver, and returns a ready-to-render
Maze with its solution attached.
"""

import sys
from typing import Set, Tuple

from mazegen.entities import Maze
from mazegen.algorithms.pattern_42 import Pattern42Injector
from mazegen.algorithms.recursive_backtracker import (
    RecursiveBacktrackerGenerator)
from mazegen.use_cases.solve_maze import MazeSolver


class GenerateMazeUseCase:
    """Orchestrates maze generation, pattern reservation,
    and solution finding."""
    def __init__(
        self,
        generator: RecursiveBacktrackerGenerator,
        solver: MazeSolver,
        pattern_injector: Pattern42Injector,
    ) -> None:
        self._generator = generator
        self._solver = solver
        self._pattern_injector = pattern_injector

    def execute(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        seed: int,
        perfect: bool
    ) -> Maze:
        """Generate a maze with the '42' pattern reserved and solve it.

        For RecursiveBacktrackerGenerator the pattern cells are reserved
        before carving, so the maze is naturally built around them. Other
        generators have the pattern injected post-hoc.

        Prints a warning to stderr if the maze is too small to fit the pattern.
        """

        reserved = self._compute_reserved(width, height)

        if entry in reserved or exit_ in reserved:
            raise ValueError("Entry or exit cannot be on the 42 pattern")

        if isinstance(self._generator, RecursiveBacktrackerGenerator):
            maze = self._generator.generate(
                width=width,
                height=height,
                entry=entry,
                exit_=exit_,
                seed=seed,
                perfect=perfect,
                reserved=reserved,
            )
            has_pattern = bool(reserved)
        else:
            maze = self._generator.generate(
                width=width,
                height=height,
                entry=entry,
                exit_=exit_,
                seed=seed,
                perfect=perfect,
            )
            has_pattern = self._pattern_injector.inject(maze)

        if not has_pattern and not reserved:
            print(
                "Warning: maze is too small to display the '42' pattern.",
                file=sys.stderr,
            )

        maze.solution = self._solver.solve(maze)
        return maze

    @staticmethod
    def _compute_reserved(width: int, height: int) -> Set[Tuple[int, int]]:
        """Return the cells reserved for the '42' pattern,
        or an empty set if it doesn't fit."""
        injector = Pattern42Injector()
        cells = injector._build_pattern_cells(width, height)
        if not injector._fits(cells, width, height):
            return set()
        return cells
