# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  renderer_ae.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: aeuvrard <aeuvrard@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/06 13:26:07 by aeuvrard        #+#    #+#               #
#  Updated: 2026/05/13 13:33:41 by aeuvrard        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from mazegen.entities import Maze
from enum import Enum
from typing import List, Tuple
from time import sleep
import sys
import termios
import tty
import a_maze_ing


PATTERN = {

    0: ["{w}██{s}{p}  {s}{w}██{s}", "{p}      {s}",
        "{w}██{s}{p}  {s}{w}██{s}"],

    1: ["{w}██████{s}", "{p}      {s}", "{w}██{s}{p}  {s}{w}██{s}"],

    2: ["{w}██{s}{p}  {s}{w}██{s}", "{p}    {s}{w}██{s}",
        "{w}██{s}{p}  {s}{w}██{s}"],

    3: ["{w}██████{s}", "{p}    {s}{w}██{s}", "{w}██{s}{p}  {s}{w}██{s}"],

    4: ["{w}██{s}{p}  {s}{w}██{s}", "{p}      {s}", "{w}██████{s}"],

    5: ["{w}██████{s}", "{p}      {s}", "{w}██████{s}"],

    6: ["{w}██{s}{p}  {s}{w}██{s}", "{p}    {s}{w}██{s}", "{w}██████{s}"],

    7: ["{w}██████{s}", "{p}    {s}{w}██{s}", "{w}██████{s}"],

    8: ["{w}██{s}{p}  {s}{w}██{s}", "{w}██{s}{p}    {s}",
        "{w}██{s}{p}  {s}{w}██{s}"],

    9: ["{w}██████{s}", "{w}██{s}{p}    {s}", "{w}██{s}{p}  {s}{w}██{s}"],

    10: ["{w}██{s}{p}  {s}{w}██{s}", "{w}██{s}{p}  {s}{w}██{s}",
         "{w}██{s}{p}  {s}{w}██{s}"],

    11: ["{w}██████{s}", "{w}██{s}{p}  {s}{w}██{s}",
         "{w}██{s}{p}  {s}{w}██{s}"],

    12: ["{w}██{s}{p}  {s}{w}██{s}", "{w}██{s}{p}    {s}", "{w}██████{s}"],

    13: ["{w}██████{s}", "{w}██{s}{p}    {s}", "{w}██████{s}"],

    14: ["{w}██{s}{p}  {s}{w}██{s}", "{w}██{s}{p}  {s}{w}██{s}",
         "{w}██████{s}"],

    15: ["{w}██████{s}", "{w}██████{s}", "{w}██████{s}"]
}


class Color(Enum):

    wall_black = "\033[30;40m"
    wall_purple = "\033[4;35m"
    wall_red = "\033[4;31m"

    path_gray = "\033[47m"
    path_yellow = "\033[46m"
    path_white = "\033[47m"

    ground_blue = "\033[4;36m"
    ground_white = "\033[4;37m"
    ground_grey = "\033[4;40m"

    entry_green = "\033[32;40m"

    exit_red = "\033[31;40m"


class Renderer():

    def __init__(self) -> None:
        self.theme = {
            "wall": [Color.wall_black.value, Color.wall_purple.value,
                     Color.wall_red.value],
            "path": [Color.path_gray.value, Color.path_yellow.value,
                     Color.path_white.value],
            "solution": [Color.ground_blue.value, Color.ground_white.value,
                         Color.ground_grey.value]
        }
        self.count_s = 0
        self.color_index = 0

    def generator(self, maze: Maze) -> None:
        """
        Entry point for the interactive maze display.

        Displays the maze and handles user input in raw terminal mode.
        Available keys: 's' (solution), 'c' (color), 'a' (animation),
        'r' (regenerate), 'q' (quit).

        Parameters
        ----------
        maze : Maze
            The maze object to display and interact with.
        """
        self.print_maze(maze, "basic")

        self.print_commands("basic")

        fd = sys.stdin.fileno()
        ancien_mode = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                key = sys.stdin.read(1)
                if key == "s":
                    self.touch_s(maze, "basic")

                elif key == "c":
                    self.touch_c(maze, "basic")

                elif key == "a":
                    self.touch_a(maze)
                    self.color_index = 0
                    self.print_maze(maze, "basic")
                    self.print_commands("basic")

                elif key == "r":
                    self.touch_r("basic")
                    break

                elif key == "q":
                    break

        except Exception as e:
            print(e)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, ancien_mode)
            print("\033[?25h")

    def touch_s(self, maze: Maze, mode: str) -> None:
        """
        Handle the 's' key press to toggle solution display.

        In basic mode, toggles between showing and hiding the solution.
        In animation mode, toggles between printing and deleting the solution.

        Parameters
        ----------
        maze : Maze
            The maze object containing the solution path.
        mode : str
            Display mode, either 'basic' or 'animation'.
        """
        if mode == "basic":
            if self.count_s % 2 == 0:
                self.find_solution_cells(maze, True)
            else:
                self.print_maze(maze, "basic")
                self.print_commands("basic")
            self.count_s += 1

        elif mode == "animation":
            if self.count_s % 2 == 0:
                self.find_solution_cells(maze, True)
                self.count_s += 1
            else:
                self.find_solution_cells(maze, False)
                self.count_s += 1

    def touch_c(self, maze: Maze, mode: str) -> None:
        """
        Handle the 'c' key press to cycle through color themes.

        Increments the color index and redraws the maze with the new theme.
        Resets to index 0 after the last available theme.

        Parameters
        ----------
        maze : Maze
            The maze object to redraw with the new color theme.
        mode : str
            Display mode, either 'basic' or 'animation'.
        """

        if mode == "basic":
            self.color_index += 1
            if self.count_s % 2 != 0:
                self.count_s += 1
            if self.color_index > 2:
                self.color_index = 0
            self.print_maze(maze, "basic")
            self.print_commands("basic")

        elif mode == "animation":
            self.color_index += 1
            if self.color_index > 2:
                self.color_index = 0

    def touch_a(self, maze: Maze) -> None:
        """
        Handle the 'a' key press to enter animation mode.

        Displays the maze with carving animation and starts a nested
        input loop for animation-specific interactions.

        Parameters
        ----------
        maze : Maze
            The maze object containing the carving history for animation.
        """
        self.print_maze(maze, "animation")
        self.print_commands("animation")
        while True:
            touche_a = sys.stdin.read(1)
            if touche_a == "s":
                self.touch_s(maze, "animation")
            elif touche_a == "c":
                self.touch_c(maze, "animation")
                self.print_maze(maze, "animation")
                self.print_commands("animation")
            elif touche_a == "q":
                break

    def touch_r(self, mode: str) -> None:
        """
        Handle the 'r' key press to regenerate a new maze.

        Calls the main entry point to generate and display a new maze,
        then resets the solution counter.

        Parameters
        ----------
        mode : str
            Display mode, currently only 'basic' is supported.
        """
        if mode == "basic":
            a_maze_ing.main()
            self.count_s = 0

    def print_maze(self, maze: Maze, mode: str) -> None:
        """
        Render the maze in the terminal using ANSI escape sequences.

        In basic mode, renders all cells at once using the current color theme.
        In animation mode, renders the '42' pattern cells first, then replays
        the carving history with a short delay between each cell.

        Parameters
        ----------
        maze : Maze
            The maze object containing cells, entry, exit, and dimensions.
        mode : str
            Display mode, either 'basic' or 'animation'.
        """
        cells = maze.cells
        print("\033[2J\033[H")

        if mode == "basic":

            for line in cells:
                for cell in line:
                    x = cell.x * 4 + 1
                    y = cell.y * 2 + 1
                    for i in range(3):
                        ligne = PATTERN[cell.walls][i]\
                            .format(w=self.theme["wall"][self.color_index],
                                    p=self.theme["path"][self.color_index],
                                    s="\033[0m")
                        print(f"\033[{y + i};{x}H{ligne}")

        elif mode == "animation":
            for line in cells:
                for cell in line:
                    if cell.is_42_pattern:
                        cx = cell.x * 4 + 1
                        cy = cell.y * 2 + 1
                        for i in range(3):
                            ligne = PATTERN[cell.walls][i].format(
                                w=self.theme["wall"][self.color_index],
                                p=self.theme["path"][self.color_index],
                                s="\033[0m",
                            )
                            print(f"\033[{cy + i};{cx}H{ligne}")

            for cx, cy in maze.carving_history:
                cell = maze.cells[cy][cx]
                sx = cell.x * 4 + 1
                sy = cell.y * 2 + 1
                for i in range(3):
                    ligne = PATTERN[cell.walls][i].format(
                        w=self.theme["wall"][self.color_index],
                        p=self.theme["path"][self.color_index],
                        s="\033[0m",
                    )
                    print(f"\033[{sy + i};{sx}H{ligne}")
                    sleep(0.004)

        entry_x = maze.entry[0]
        entry_y = maze.entry[1]

        x = entry_x * 4 + 3
        y = entry_y * 2 + 2
        print(f"\033[{y};{x}H{Color.entry_green.value}██\033[0m")

        exit_x = maze.exit[0]
        exit_y = maze.exit[1]

        x = exit_x * 4 + 3
        y = exit_y * 2 + 2
        print(f"\033[{y};{x}H{Color.exit_red.value}██\033[0m")

        nbr_line = maze.height * 2 + 2

        print(f"\033[{nbr_line};0H")
        print("\033[?25h")

    def print_solution(self, maze: Maze, solution: List[Tuple[int, int]],
                       delete: bool) -> None:
        """
        Render or erase the solution path on the maze display.

        Draws the solution path cell by cell with a short delay, connecting
        each step with an intermediate character between adjacent cells.
        Skips the entry and exit cells to preserve their colored markers.

        Parameters
        ----------
        maze : Maze
            The maze object containing entry, exit coordinates and dimensions.
        solution : List[Tuple[int, int]]
            Ordered list of (y, x) coordinates forming the solution path.
        delete : bool
            If True, erases the solution by drawing path-colored spaces.
            If False, draws the solution with solution-colored blocks.
        """
        x_entry = (maze.entry[0] * 4) + 3
        y_entry = (maze.entry[1] * 2) + 2

        x_exit = (maze.exit[0] * 4) + 3
        y_exit = (maze.exit[1] * 2) + 2

        if delete:
            path = solution[::-1]
            theme = "path"
            glyph = "  "
        else:
            path = solution
            theme = "solution"
            glyph = "██"

        for nb, coordinates in enumerate(path):
            coor_x = coordinates[1]
            coor_y = coordinates[0]
            x = coor_x * 4 + 3
            y = coor_y * 2 + 2
            if (x, y) not in ((x_entry, y_entry), (x_exit, y_exit)):
                print(f"\033[{y};{x}H{self.theme[theme][self.color_index]}"
                      f"{glyph}\033[0m")
            try:
                coor_x_p1 = path[nb + 1][1]
                coor_y_p1 = path[nb + 1][0]
                x_p1 = (coor_x_p1 - coor_x) * 2 + x
                y_p1 = (coor_y_p1 - coor_y) + y
                print(f"\033[{y_p1};{x_p1}H"
                      f"{self.theme[theme][self.color_index]}{glyph}\033[0m")
            except IndexError:
                pass
            sleep(0.02)

        nbr_line = maze.height * 2 + 8

        sys.stdout.write(f"\033[{nbr_line};0H")
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def find_solution_cells(self, maze: Maze, print_solution: bool) -> None:
        """
        Compute the solution coordinates from the maze solution string.

        Parses the solution string (N, E, S, W letters) starting from
        the entry point and builds the list of visited coordinates,
        then delegates rendering to print_solution.

        Parameters
        ----------
        maze : Maze
            The maze object containing the solution string and entry point.
        print_solution : bool
            If True, displays the solution path.
            If False, erases the solution path.
        """
        solution = maze.solution
        x = maze.entry[0]
        y = maze.entry[1]
        coordinates = []

        coordinates.append((y, x))
        for letter in solution:
            if letter == "N":
                y -= 1
            elif letter == "E":
                x += 1
            elif letter == "S":
                y += 1
            elif letter == "W":
                x -= 1
            coordinates.append((y, x))
        if print_solution:
            self.print_solution(maze, coordinates, False)
        else:
            self.print_solution(maze, coordinates, True)

    def print_commands(self, mode: str) -> None:
        """
        Display the available keyboard commands in the terminal.

        Uses sys.stdout.write with carriage returns to correctly render
        text in raw terminal mode.

        Parameters
        ----------
        mode : str
            Display mode, either 'basic' or 'animation'. Determines which
            set of commands is shown.
        """
        if mode == "basic":
            sys.stdout.write("Welcome to A maze ing :)\r\n")
            sys.stdout.write("'s': to print/delete the solution\r\n")
            sys.stdout.write("'c': to change maze Color\r\n")
            sys.stdout.write("'a': to access animation\r\n")
            sys.stdout.write("'r': to re-generate a new maze\r\n")
            sys.stdout.write("'q': to leave\r\n")
        elif mode == "animation":
            sys.stdout.write("Welcome to A maze ing animation !!!\r\n")
            sys.stdout.write("'s': to print/delete the solution\r\n")
            sys.stdout.write("'c': to change maze Color\r\n")
            sys.stdout.write("'q': to leave animation\r\n")
