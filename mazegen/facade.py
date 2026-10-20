"""Public facade for the mazegen package.

Provides a single, simple entry point (`MazeGenerator`) that wires together
the generator, solver and pattern injector. Designed to be the only class
external users of the pip-installable mazegen package need to import.

Basic usage:
    >>> from mazegen.facade import MazeGenerator
    >>> gen = MazeGenerator(width=20, height=15, seed=42)
    >>> maze = gen.generate()
    >>> grid = gen.get_hex_grid()
    >>> path = gen.get_solution_path()
"""

import random
from typing import List, Optional, Tuple

from mazegen.algorithms.pattern_42 import Pattern42Injector
from mazegen.algorithms.recursive_backtracker import (
    RecursiveBacktrackerGenerator)
from mazegen.entities import Maze
from mazegen.use_cases.generate_maze import GenerateMazeUseCase
from mazegen.use_cases.solve_maze import MazeSolver


class MazeGenerator:
    """High-level facade: configure a maze, generate it, access its data."""

    def __init__(
        self,
        width: int = 20,
        height: int = 15,
        entry: Optional[Tuple[int, int]] = None,
        exit_: Optional[Tuple[int, int]] = None,
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        """Configure the generator without running it yet.

        `entry` defaults to the top-left corner, `exit_` to the bottom-right.
        Omit `seed` to get a random one — call `.seed` afterwards
        to retrieve it.
        """

        self._width = width
        self._height = height
        self._entry: Tuple[int, int] = entry if entry is not None else (0, 0)
        self._exit: Tuple[int, int] = (
            exit_ if exit_ is not None else (width - 1, height - 1)
        )
        self._seed: int = (seed if seed is not None
                           else random.randint(0, 2**31))
        self._perfect = perfect
        self._use_case = GenerateMazeUseCase(
            generator=RecursiveBacktrackerGenerator(),
            solver=MazeSolver(),
            pattern_injector=Pattern42Injector(),
        )
        self._maze: Optional[Maze] = None

    def generate(self) -> Maze:
        """Build the maze and return it. Also caches it for later access."""
        self._maze = self._use_case.execute(
            width=self._width,
            height=self._height,
            entry=self._entry,
            exit_=self._exit,
            seed=self._seed,
            perfect=self._perfect,
        )
        return self._maze

    @property
    def maze(self) -> Maze:
        """The most recently generated Maze.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if self._maze is None:
            raise RuntimeError("Call generate() before accessing the maze.")
        return self._maze

    def get_hex_grid(self) -> List[str]:
        """Return the maze as a list of hex-encoded row strings."""
        return self.maze.to_hex_grid()

    def get_solution_path(self) -> List[str]:
        """Return the solution as a list of N/E/S/W letters."""
        return self.maze.solution

    @property
    def seed(self) -> int:
        """The seed used for generation (random if none was provided)."""
        return self._seed
