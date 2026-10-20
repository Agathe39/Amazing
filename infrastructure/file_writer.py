from mazegen.entities import Maze


class TextMazeWriter:
    """Writes a solved maze to a UTF-8 text file in hex-grid format.

    Output format:
        - One hex digit per cell, rows separated by newlines.
        - A blank line separator.
        - Entry coordinates as 'x,y'.
        - Exit coordinates as 'x,y'.
        - Solution path as a string of N/E/S/W letters.
    """
    def write(self, maze: Maze, output_path: str) -> None:
        """Write the maze grid, coordinates and solution path to a file.

        Raises:
            IOError: If the file cannot be opened or written.
        """
        try:
            with open(output_path, "w", encoding="utf-8", newline="\n") as f:
                for row in maze.to_hex_grid():
                    f.write(row + "\n")
                f.write("\n")
                ex, ey = maze.entry
                f.write(f"{ex},{ey}\n")
                xx, xy = maze.exit
                f.write(f"{xx},{xy}\n")
                f.write("".join(maze.solution) + "\n")
        except OSError as exc:
            raise IOError(
                f"Cannot write maze to '{output_path}': {exc}"
            ) from exc
