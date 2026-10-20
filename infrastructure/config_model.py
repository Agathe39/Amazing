"""Configuration parser for maze generation.

Loads and validates maze parameters from a KEY=VALUE text file.
Supports '#' comments and blank lines.

Usage:
    config = MazeConfigModel.from_file("config.txt")
    print(config.WIDTH, config.HEIGHT)
    seed = config.effective_seed()

Config file format (KEY=VALUE, one per line, # = comment):
    WIDTH=20
    HEIGHT=15
    ENTRY=0,0
    EXIT=19,14
    OUTPUT_FILE=maze.txt
    PERFECT=True
    SEED=42                         # optional — omit for random
"""
from dataclasses import dataclass
import os
import random
from typing import Any, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator

_MANDATORY_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT",
                   "OUTPUT_FILE", "PERFECT"}


@dataclass
class MazeConfig:
    """Domain object holding validated maze generation parameters.

    Produced by MazeConfigModel.from_file() and consumed by the rest of
    the application. SEED is always a concrete integer here — never None.
    """
    width: int
    height: int
    entry: Tuple[int, int]
    exit_: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: int


class MazeConfigModel(BaseModel):
    """Pydantic model for loading and validating maze configuration files.

    Use from_file() as the main entry point — it handles file reading,
    mandatory-key checking, and conversion to the MazeConfig dataclass.
    Optional keys fall back to their defaults when absent from the file.
    """
    WIDTH: int = Field(ge=2, le=30)
    HEIGHT: int = Field(ge=2, le=30)
    ENTRY: Tuple[int, int]
    EXIT: Tuple[int, int]
    OUTPUT_FILE: str = Field(min_length=1, max_length=20)
    PERFECT: bool = Field(default=True)
    SEED: int = Field(default_factory=lambda: random.randint(0, 2**31 - 1))

    @field_validator("ENTRY", "EXIT", mode="before")
    @classmethod
    def parse_coords(cls, v: Any) -> Tuple[int, int]:
        """Parse an 'x,y' string into a (int, int) tuple.

        Raises:
            ValueError: If not 'x,y' format, values aren't integers,
                or either coordinate is negative.
        """
        if isinstance(v, tuple):
            return v
        parts = v.split(",")
        if len(parts) != 2:
            raise ValueError(f"must be 'x,y' format, got {v!r}")
        try:
            x, y = int(parts[0].strip()), int(parts[1].strip())
        except ValueError:
            raise ValueError(f"coordinates must be integers, got {v!r}")
        if x < 0 or y < 0:
            raise ValueError(f"coordinates must be non-negative,"
                             f" got ({x}, {y})")
        return (x, y)

    @field_validator("PERFECT", mode="before")
    @classmethod
    def parse_bool(cls, v: Any) -> bool:
        """Accept true/false/yes/no/1/0 (case-insensitive)
        in addition to bool."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes"):
                return True
            if v.lower() in ("false", "0", "no"):
                return False
        raise ValueError(f"must be a boolean (true/false/yes/no/0/1),"
                         f" got {v!r}")

    @field_validator("SEED", mode="before")
    @classmethod
    def parse_seed(cls, v: Any) -> Optional[int]:
        """Generate a random seed if absent, otherwise parse as int."""
        if v is None or v == "":
            return random.randint(0, 2**31 - 1)
        try:
            return int(v)
        except (TypeError, ValueError):
            raise ValueError(f"SEED must be an integer, got {v!r}")

    @model_validator(mode="after")
    def validate_entry_exit(self) -> "MazeConfigModel":
        """Validate that ENTRY and EXIT are distinct and within maze bounds."""
        if self.ENTRY == self.EXIT:
            raise ValueError("ENTRY and EXIT must be different")
        x1, y1 = self.ENTRY
        x2, y2 = self.EXIT
        if x1 >= self.WIDTH or x2 >= self.WIDTH:
            raise ValueError(f"Entry/Exit X exceeds maze width ({self.WIDTH})")
        if y1 >= self.HEIGHT or y2 >= self.HEIGHT:
            raise ValueError(f"Entry/Exit Y exceeds maze"
                             f"height ({self.HEIGHT})")
        return self

    def to_maze_config(self) -> MazeConfig:
        """Convert to a MazeConfig dataclass,
        resolving SEED to a concrete int."""
        return MazeConfig(
            width=self.WIDTH,
            height=self.HEIGHT,
            entry=self.ENTRY,
            exit_=self.EXIT,
            output_file=self.OUTPUT_FILE,
            perfect=self.PERFECT,
            seed=self.SEED
        )

    @classmethod
    def from_file(cls, path: str) -> "MazeConfig":
        """Load and validate maze configuration from a KEY=VALUE text file.

        Performs an early check for mandatory keys so missing fields are
        reported by name rather than relying on Pydantic's generic 'field
        required' error. On success, returns a MazeConfig dataclass ready
        for use by the rest of the application.

        Args:
            path: Path to the configuration file.

        Returns:
            A validated and converted MazeConfig dataclass instance.

        Raises:
            FileNotFoundError: If the file does not exist at the given path.
            ValueError: If mandatory keys are missing or the file cannot be
                read.
            ValidationError: If any field value fails Pydantic validation.
        """
        pairs = cls._scan_file(path)
        missing = _MANDATORY_KEYS - pairs.keys()
        if missing:
            raise ValueError(
                f"Missing mandatory config keys: {', '.join(sorted(missing))}"
            )
        return cls.model_validate(pairs).to_maze_config()
        # return cls(**pairs).to_maze_config()

    @staticmethod
    def _scan_file(path: str) -> dict[str, str]:
        """Read a KEY=VALUE file and return a dict
        of uppercase key → raw value.

        Skips blank lines and '#' comments. Raises ValueError on malformed
        lines and OSError on read failure.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Configuration file not found: {path!r}")
        pairs: dict[str, str] = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if "=" not in stripped:
                        raise ValueError(
                            f"Line {line_num}: expected KEY=VALUE,"
                            f" got: {stripped!r}"
                        )
                    key, _, value = stripped.partition("=")
                    pairs[key.strip().upper()] = value.strip()
        except OSError as exc:
            raise ValueError(f"Cannot read {path!r}: {exc}") from exc
        return pairs
