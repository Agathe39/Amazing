import sys

from mazegen.algorithms.pattern_42 import Pattern42Injector
from mazegen.algorithms.recursive_backtracker import (
    RecursiveBacktrackerGenerator)
from mazegen.entities import Maze
from mazegen.use_cases.generate_maze import GenerateMazeUseCase
from mazegen.use_cases.solve_maze import MazeSolver

from infrastructure.config_model import MazeConfigModel, MazeConfig
from infrastructure.file_writer import TextMazeWriter
from infrastructure.renderer import renderer_ansi

from pydantic import ValidationError


def _build_use_case() -> GenerateMazeUseCase:
    return GenerateMazeUseCase(
        generator=RecursiveBacktrackerGenerator(),
        solver=MazeSolver(),
        pattern_injector=Pattern42Injector(),
    )


def _generate(config: MazeConfig) -> Maze:
    return _build_use_case().execute(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit_=config.exit_,
        seed=config.seed,
        perfect=config.perfect,
    )


def _write(maze: Maze, path: str) -> None:
    TextMazeWriter().write(maze, path)


def _run_renderer(config: MazeConfig, maze: Maze) -> None:
    current_seed = [config.seed]
    print(f"Seed: {current_seed[0]}")
    renderer = renderer_ansi.Renderer()
    renderer.generator(maze)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
        return 1
    try:
        try:
            config = MazeConfigModel.from_file(sys.argv[1])
        except FileNotFoundError as exc:
            print(f"Configuration error: {exc}", file=sys.stderr)
            return 1
        except ValidationError as exc:
            first = exc.errors()[0]
            field = ".".join(str(p) for p in first["loc"])
            msg = first["msg"].removeprefix("Value error, ")
            print(f"Configuration error in {field}: {msg}", file=sys.stderr)
            return 1
        except ValueError as exc:
            print(f"Configuration error: {exc}", file=sys.stderr)
            return 1
        try:
            maze = _generate(config)
        except ValueError as exc:
            print(f"Maze generation error: {exc}", file=sys.stderr)
            return 1
        try:
            _write(maze, config.output_file)
            print(f"Maze written to '{config.output_file}'.")
        except IOError as exc:
            print(f"File write error: {exc}", file=sys.stderr)
            return 1
        _run_renderer(config, maze)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
